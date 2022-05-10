#include "sfp.h" 
#include <stdlib.h>

/*
IEEE half-precision format 
Sign
1 : negative  
0 : positive 
------------------------------- 
Exponent & Mentissa 

E == 31: 11111 (5 bits) 
     T == 0 : Signed Infinity 
     T != 0 : NaN 

0<E<31:
     (-1)^S X 2^(E-15) X (1+2^(-10) X T))

E == 0:
     T == 0 : signed zero 
     T != 0 : (-1)^s x 2^(-14) x (0 + (2^(-10) x T))  
-------------------------------
*/ 

const sfp POSINF = 0b0111110000000000;
const sfp NEGINF = 0b1111110000000000;
const sfp NAN    = 0b1111111111111111;
const sfp ZERO   = 0b0000000000000000;


/*@brief converts int to 16 bit (==short) sfp */ 
/* retain sign bit and manipulate the other 15 bits */ 
sfp int2sfp(int input) 
{
    // > maximum of sfp 
    if(input > 65504)  return POSINF; //0b0111110000000000;
    // < minimum of sfp 
    if(input < -65504) return NEGINF;
    // int 0
    if(input == 0)     return ZERO;
    
    sfp msb; 
    unsigned int mantissa = (input & 0x7FFFFFFF); 
    int tmp = mantissa; 
    unsigned short exponent = 0; 
    sfp exp = 0;

    // check msb
    if((input & 0x80000000) == 0x80000000)
    { 
        msb = 0x01 << 15;
    }
    else 
    { 
        msb = 0;
    }
    // return highest index from number
    for (int i = 0; i < 31; i++) 
    {
        if (tmp % 2 == 1) exponent = i;
        tmp /= 2;
    }
    // remove implied 1
    mantissa = mantissa & ~(0x01 << exponent); 
    exp = 15 + exponent;
    // shift left
    exp = exp << 10;
    
    
    return msb | exp | (mantissa << (10 - exponent));
}



int sfp2int(sfp input)
{
    // positive infinity input
    if (input == 0b0111110000000000) return  2147483647;
    // negative infinity input 
    if (input == 0b1111110000000000) return -2147483648;
    // +- NaN Input
    if (input == 0b1111111111111111) return -2147483648;
    if (input == 0b0111111111111111) return -2147483648;
    
    sfp sign;
    sfp exponent;
    int e;
    int mul = 1;
    sfp mantissa;
    int m = 0;
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
    
    int powtwo;
    if(sign == 0x8000) powtwo = -1;
    else powtwo = 1;
    
    // use mathemetical expression v=m*2^e
    for (int i = 0; i < e; i++)
    {
        powtwo = powtwo * 2;
    }
    // add implied one and recalculate fraction
    result = powtwo + (powtwo * m)/1024;
    return result;
}



/* @brief 32bit single precision fp to 16bit sfp  */
sfp float2sfp(float input)
{
     
     // > maximum of sfp 
     if(input > 32736)   return POSINF;
     // < minimum of sfp 
     if(input < -32736)  return NEGINF;
     // int 0
     if(input == 0)      return ZERO;
     
     // binary value of input must be converted to integer type
     int val = *(int*)&input;
     
     // extract bits and shift all to LSB
     int sign = (val & 0x80000000) >> 16;
     int exponent = ((val >> 23) & 0xFF) - 127 + 15;  // exponent - f32_bias + f16_bias
     int mantissa = (val & 0x7FFFFF) >> 13; 
     
     if(mantissa == 0x00) return ZERO;
     
     return (sign | (exponent << 10) | mantissa);    
}


/* @brief 16 bit sfp to 32 bit single precision fp */
float sfp2float(sfp input)
{
     if(input == 0x0000) return 0x00000000;
     else if(input == 0b1111111111111111) return 0x7FC00000;  // NaN
     else if(input == 0b0111110000000000) return 0x7F800000;  // posinf
     else if(input == 0b1111110000000000) return 0xFF800000;  // neginf
     
     // extract bits and shift all to LSB
     int sign = input & 0x8000; 
     int exponent = ((input >> 10) & 0x001F) - 15 + 127;
     int mantissa = input & 0x03FF;
     
     int result = sign << 16 | exponent << 23 | mantissa << 13;
     
     float output = *(float*)&result;
     return output;
}


int countDigit(sfp input)
{
     sfp tmp = input;
     int cnt = 0;
     while(tmp > 0)
     {
          tmp = tmp >> 1;
          cnt++;
     }
     // working with 10bit + hidden, do not count hidden
     return cnt;
}


/* @brief 16 bit sfp addition */
sfp sfp_add(sfp a, sfp b)
{
     // handling NAN first
     if(a == NAN || b == NAN)                return NAN;
     // positive & negative infinity 
     else if(a == POSINF && b == NEGINF)     return NAN;
     else if(a == NEGINF && b == POSINF)     return NAN;
     // resulting in Positive infinity
     else if(a == POSINF && b != NEGINF)     return POSINF;
     else if(a != NEGINF && b == POSINF)     return POSINF;
     // resulting in negative infinity
     else if(a == NEGINF && b != POSINF)     return NEGINF;
     else if(a != POSINF && b == NEGINF)     return NEGINF;
     // end  POSINF-POSINF / NEGINF-NEGINF case handled
     
     // first, make sure a is greater than b by swapping values
     if ((b & 0x7CFF) > (a & 0x7CFF)) // 0111 1111 1111 1111
     {
        sfp tmp;
        tmp = a;
        a = b;
        b = tmp;
     }
     sfp sA = a & 0x8000;
     sfp sB = b & 0x8000;
     sfp eA = (a & 0x7C00) >> 10; // 0111 1100 0000 0000
     sfp eB = (b & 0x7C00) >> 10;
     sfp mA = (a & 0x03FF); // 0000 0011 1111 1111
     sfp mB = (b & 0x03FF);
     sfp sR = 0;
     sfp eR = eA;
     sfp mR;
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
     else mB = mB | 0x0400;
     // show hidden 1 on mA
     mA = mA | 0x0400; //  0000 0100 0000 0000
     
     // addition or subtraction
     if(sA == 0x8000 && sB == 0x8000)
     {
          mR = mA + mB; 
          sR = 0x8000;
     }
     else if(sA == 0x8000 || sB == 0x8000)
     {
          mR = mA - mB;
          if(sA == 0x8000) sR = 0x8000;
     }
     else mR = mA + mB;
     
     // normalize result - for msb (implied) greater or less than 1
     sfp tmp = mR;
     while( (tmp & 0xFFFFFC00) > 0x01) // 0000 0100 0000 0000
     {
          tmp = tmp >> 1; 
          eR = eR + 0x01;
     }
     while( (tmp & 0xFFFFFC00) < 0x01)
     {
          tmp = tmp << 1;
          eR = eR - 0x01;
     }
     
     // round to even 
     int numDigit = countDigit(mR);   
     int lsbReference = 0x01 << (numDigit - 10); 
     int isOdd = mR & lsbReference; 
     int toLoseReference = mR & (0x01 << (numDigit - 11));
     if (numDigit > 10)
     {

         int bitsToRound = 0x00;
         for (int i = 0; i < (numDigit - 11); i++)
         {
             bitsToRound = bitsToRound | 0x01;
             bitsToRound = bitsToRound << 1;
         }
         //bitsToRound = bitsToRound >> 1;
         bitsToRound = mR & bitsToRound;
         // greater than half
         if (bitsToRound > toLoseReference)
         {
             mR = mR + lsbReference;
         }
         // exactly half
         else if (bitsToRound == toLoseReference)
         {
             if(isOdd)
             {
                 mR = mR + lsbReference;     
             }
         }
         // less than zero
         else { }
     }
     
     // shift
     int shift = numDigit - 11;
     if(shift < 0) mR = mR << (-1 * shift);
     if(shift > 0) mR = mR >> shift;
     
     mR = mR & 0x03FF; // 0000 0011 1111 1111 remove hidden bit

     return sA | (eR << 10) | mR;
}


sfp sfp_mul(sfp a, sfp b)
{
     
     // handling NAN first
     if(a == NAN || b == NAN)                return NAN;
     // infinity with zero 
     else if(a == POSINF && b == 0)          return NAN;
     else if(a == 0 && b == POSINF)          return NAN;
     else if(a == NEGINF && b == 0)          return NAN;
     else if(a == 0 && b == POSINF)          return NAN;
     // infinity with infinity
     else if(a == POSINF && b == POSINF)     return POSINF;
     else if(a == POSINF && b == NEGINF)     return NEGINF;
     else if(a == NEGINF && b == POSINF)     return NEGINF;
     else if(a == NEGINF && b == NEGINF)     return POSINF;
     // normal value with posinf
     else if(a == POSINF && b != NEGINF)     return POSINF;
     else if(a != NEGINF && b == POSINF)     return POSINF;
     // normal value with neginf
     else if(a == NEGINF && b != POSINF)     return NEGINF;
     else if(a != POSINF && b == NEGINF)     return NEGINF;
     // end  POSINF-POSINF / NEGINF-NEGINF case handled

     // check for zero 
     if(a == 0 || b == 0) return ZERO;     

     unsigned int sA = (a & 0x8000) >> 15; 
     unsigned int sB = (b & 0x8000) >> 15;
     int eA = (a & 0x7C00) >> 10;  // 0111 1100 0000 0000
     int eB = (b & 0x7C00) >> 10;  
     int mA = (a & 0x03FF);  // 0000 0011 1111 1111 
     int mB = (b & 0x03FF);  
     
     unsigned int sR = sA ^ sB;  // resultant sign
     int eR = (eA - 15) + (eB - 15) + 15;  // add true exponent and rebias
     
     // show hidden bit on mantissa 
     mA = mA | 0x0400; 
     mB = mB | 0x0400;
     // multiply mantissa 
     // 11 bit * 11 bit results in 22 bit binary, 
     // of which right 20 bits are below the binary point
     int mR = (mA * mB);
     int b4BinaryPoint = (mR & 0xFFF00000) >> 20;  // 1111 1111 1111 0000 0000 0000 0000 0000 
     int afterBinaryPoint = mR & 0x000FFFFF;
     // normalize
     while(b4BinaryPoint > 0x01) 
     {
          b4BinaryPoint = b4BinaryPoint >> 1;
          mR = mR >> 1;  // make sure 20 digit below b.p. 
          eR = eR + 1;
     }
     while( b4BinaryPoint < 0x01)
     {
          b4BinaryPoint = b4BinaryPoint << 1;
          mR = mR << 1;
          eR = eR - 1;
     }
     // round to even and shift
     int isNearestOdd = (mR & 0x0400) >> 10;  
     int bottom10Bit = (mR & 0x03FF);
     if(bottom10Bit > 0x0200)  // greater 
     {
          mR = mR + 0x0400;
     }
     else if(bottom10Bit == 0x0200)
     {
          if(isNearestOdd) mR = mR + 0x0400;
     }
     else { }  // smaller  
     
     mR = mR >> 10;
     // hide hidden bit
     mR = mR & 0x03FF;  // 0000 0011 1111 1111
     
     return (sR << 15) | (eR << 10) | mR; 
}


/* @brief used to return the bit stream of sfp data type */ 
/* remember sfp is of data type short */ 
char* sfp2bits(sfp result) 
{
     sfp tmp = result; char *bitStream = malloc(sizeof(char) * 16);
     // push binary to sfp and count the number of index
     tmp = tmp >> 8; 
     for(int i = 7; i >= 0; i--) {
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



