#include <stdio.h>
#include <stdlib.h>

typedef unsigned short sfp;

/* @brief used to return the bit stream of sfp data type */
/* remember sfp is of data type short                    */
/* do not confuse number of binary index and number of array size required */

char* sfp2bits(sfp result)
{
    sfp tmp = result;
    char *bitStream = malloc(sizeof(char) * 16);
    // push binary to sfp and count the number of index
    tmp = tmp >> 8;
    for(int i = 7; i >= 0; i--)
    {
        if ((tmp & 0x01) == 1)  
            bitStream[i] = '1';
        else
            bitStream[i] = '0';
        tmp = tmp >> 1;
    }
    tmp = result;
    for(int i = 15; i >= 8; i--)
    {
        if ((tmp & 0x01) == 1)
            bitStream[i] = '1';
        else
            bitStream[i] = '0';
        tmp = tmp >> 1;
    }
    return bitStream;
}

/* @brief converts integer to small floating point  */
sfp int2sfp(int input)
{
    sfp msb;
    unsigned int notMsb = (input & 0x7FFFFFFF);
    unsigned int tmp = notMsb;
    unsigned short index = 0;
    sfp exponent = 0;
    sfp exp = 0;
    // check msb 
    if((input & 0x80000000) == 0x80000000){
        msb = 0x01 << 15;
    }
    else {
        msb = 0;
    }
    // return highest index from number
    for (int i = 0; i < 31; i++)
    {
        if (tmp % 2 == 1)
        {
            exponent = i;
        }
        tmp /= 2;
    }
    // remove implied 1
    notMsb = notMsb & ~(0x01 << exponent);
    index--;
    exp = 15 + exponent;
    // shift left
    exp = exp << 10;


    return msb | exp | (notMsb << (10 - exponent));
}

int sfp2int(sfp input)
{
    sfp sign;
    sfp exponent;
    unsigned int e;
    unsigned int mul = 1;
    sfp mantissa;
    unsigned int m = 0;
    int result;
    // extract sign, exponent, mantissa
    sign = (0x8000 & input);
    exponent = (input & 0x7C00) >> 10;
    mantissa = (input & 0x03FF);

    // exponent
    e = exponent - 15;

    // mantissa
    for (int i = 0; i < 10; i++)
    {
        mul = mul * 2;
        if ((mantissa & 0x0200) == 0x0200)
        {
            // equalize divisor
            m = m + 1024 / mul;
        }
        mantissa = mantissa << 1;
    }
    
    int powtwo = 1;
    // use mathemetical expression v=m*2^e
    for (int i = 0; i < e; i++)
    {
        powtwo = powtwo * 2;
    }
    // add implied one and recalculate fraction
    result = powtwo + (powtwo * m)/1024;
    printf("%d\n", result);
    return result;
}

sfp float2sfp(float input)
{
    // convert float type to binary
    int val = *(int *)&input;

    // extract bits and shift all to LSB
    int sign = (val & 0x80000000) >> 16;
    int exponent = (val >> 23) & 0xFF - 127 + 15; // exponent - f32_bias + f16_bias
    int mantissa = (val & 0x7FFFFF) >> 13;

    printf("sign 0x%x\n", sign);
    printf("exponent 0x%x\n", exponent);
    printf("mantissa 0x%x\n", mantissa);

    return sign | exponent << 7 | mantissa;
}

float sfp2float(sfp input)
{
    // extract bits and shift all to LSB
    int sign = input & 0x8000;
    int exponent = ((input >> 10) & 0x001F) - 15 + 127;
    int mantissa = input & 0x03FF;

    printf("sign %x\n", sign<<16);
    printf("exp %x\n", exponent<<23);
    printf("mantissa %x\n", mantissa<<13);

    int result = (sign << 16) | (exponent << 23) | (mantissa << 13);

    printf("result %x\n", result);
    
    return result;
}

sfp sfp_add(sfp a, sfp b)
{
    // first, make sure a is greater than b by swapping values
    if ((b & 0x7CFF) > (a & 0x7CFF)) // 0111 1111 1111 1111
    {
        sfp tmp; 
        tmp = a;
        a = b;
        b = tmp;
    }
    int sA = a & 0x8000;
    int sB = b & 0x8000;
    int eA = (a & 0x7C00) >> 10; // 0111 1100 0000 0000
    int eB = (b & 0x7C00) >> 10;
    int mA = (a & 0x03FF); // 0000 0011 1111 1111
    int mB = (b & 0x03FF);
    int sR;
    int eR = eA;
    int mR;
    int shiftBy = eA - eB;
    // align exponent
    if (shiftBy)
    {
        // shift mb by 1 (hidden bit considered)
        mB = mB >> 1;
        mB = mB | 0x0200; //  0000 0010 0000 0000
        shiftBy--;
        // shift mb by shiftBy-1
        mB = mB >> shiftBy;
    }
    else
        mB = mB | 0x0400;
    // show hidden 1 on mA
    mA = mA | 0x0400; //  0000 0100 0000 0000
    // addition or subtraction
    mA = mA | 0x0400; 
    if( (sA == 0x8000) && (sB == 0x8000) )
    {
        mR = mA + mB;
        sR = 0x8000;
    }
    else if(sA == 0x8000 || sB == 0x8000)
    {
        // mA Greater than mB so subtract
        mR = mA - mB; 
        // if mA is negative, expression will be negative  
        if(sA == 0x8000) sR = 0x8000;
    }
    else mR = mA + mB;
    // normalize result - for msb (implied) greater or less than 1
    while ((mR & 0xFC00) > 0x0400) // 1111 1100 0000 0000
    {
        mR = mR >> 1;
        eR = eR + 0x01;
    }
    while ((mR & 0xFC00) < 0x0400)
    {
        mR = mR << 1;
        eR = eR - 0x01;
    }

    //mR = mR & 0x03FF; // 0000 0011 1111 1111

    return sR | (eR << 10) | mR;
}

sfp sfp_mul(sfp a, sfp b)
{
    unsigned int sA = (a & 0x8000) >> 15;
    unsigned int sB = (b & 0x8000) >> 15;
    int eA = (a & 0x7C00) >> 10; // 0111 1100 0000 0000
    int eB = (b & 0x7C00) >> 10;
    int mA = (a & 0x03FF); // 0000 0011 1111 1111
    int mB = (b & 0x03FF);

    unsigned int sR = sA ^ sB;           // resultant sign
    int eR = (eA - 15) + (eB - 15) + 15; // add true exponent and rebias

    // check for zero
    if (a == 0x0000 || b == 0x0000)
        return 0x0000;

    // show hidden bit on mantissa
    mA = mA | 0x0400;
    mB = mB | 0x0400;
    // multiply mantissa
    // 11 bit * 11 bit results in 22 bit binary,
    // of which right 20 bits are below the binary point
    int mR = (mA * mB);
    int b4BinaryPoint = (mR & 0xFFF00000) >> 20; // 1111 1111 1111 0000 0000 0000 0000 0000

    // normalize
    while (b4BinaryPoint > 0x01)
    {
        b4BinaryPoint = b4BinaryPoint >> 1;
        eR = eR + 1;
    }
    while (b4BinaryPoint < 0x01)
    {
        b4BinaryPoint = b4BinaryPoint << 1;
        eR = eR - 1;
    }
    // round
    while ((mR & 0xFFFFFC00) > 0x0400) // 1111 1100 0000 0000
    {
        mR = mR >> 1;
    }

    // hide hidden bit
    mR = mR & 0x03FF; // 0000 0011 1111 1111

    return (sR << 15) | (eR << 10) | mR;
}

int main()
{
    sfp a = 0b0100101110000000;
    sfp b = 0b0100101110000000;
    //char* expected = "1011111110100000"

    printf("digit of a: %d\n", countDigit(0b0101100000));
    printf("digit of b: %d\n", countDigit(0b1110000000));

    sfp_mul(a, b);
    //printf("%s", sfp2bits(result));

    return 0;
}

// actual   0000 0110 1011 0000 0000 0000 0000 0000  
// expected 0011 1110 1011 0000 0000 0000 0000 0000