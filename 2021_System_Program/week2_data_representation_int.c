#include <stdio.h>

int main(){
    unsigned i;
    int a[3] = {1, 2, 3};
    for(i = sizeof(a)/sizeof(int) - 1; i >= 0; i--)
        printf("%d\n", a[i]);
    return 0;
}

/*
on gcc (intel Macbook Pro, VSCode) output is
/bin/sh: line 1: 82161 Illegal instruction: 4 "/Users/jihwan/Desktop/Learning/2021_System_Program/"data_representation_int

on MSVC (visual studio, AMD64 bit) output is
3
2
1
-858993460
-858993460
... 

Reasoning:
for(i = sizeof(a) / sizeof(int) - 1; i >= 0; i--) indicates that 'i' will start from unsigned representation 2,
as sizeof(a) = 4byte * 3, and sizeof(int) = 4. Variable i decreases in the following sequence : 2, 1, 0 ... .
However, because it is of unsigned type, 0 - 1 is not interpreted as a negative number (it would be a very large positive number).
An easy way to re-check this conjecture is to run the following program :

#include <stdio.h>
int main() {
     unsigned i = 0;
     printf("%u", i - 1);
     return 0;
}
output : 4294967295
Hence, we can see that the output from pg20 when i is below 0 is some garbage value at memory location 4294967295 ... 
*/
