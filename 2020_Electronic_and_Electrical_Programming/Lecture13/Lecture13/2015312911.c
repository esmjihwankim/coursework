//
//  main.c
//  Lecture13
//
//  Created by Jihwan Kim on 2020/06/05.
//  Copyright © 2020 LogicLead. All rights reserved.
//


/*
//A more proper way of using the global variable is to use global array
#include <stdio.h>

void roots(double);
double ans[2] = {0, 0};

int main(){
    
    float x = 10;
    roots(x);
    printf("square root of %f is %f\n", x, ans[0]);
    printf("square root of %f is %f\n", x, ans[1]);
    
    system("pause");
}

void roots(double y){
    ans[0] = sqrt(y);
    ans[1] = -1 * sqrt(y);
}
*/


/*
#include <stdio.h>

void roots(float, float *pans);

int main(void){
    
    float x = 10;
    float a[2] = {0, 0}, *pa = &a;
     
    roots(x, pa);
    printf("square root of %f is %f @ %x\n", x, *pa, pa);
    printf("square root of %f is %f @ %x\n", x, *(pa + 1), (pa + 1));
    system("pause");
}

void roots(float y, float * pans){
    *pans = sqrt(y);
    *(pans+1) = -1 * sqrt(y);
   }
*/

//printf function destroys the next value of a pointer

 


/*
//multiple value return by structure
#include <stdio.h>
#include <math.h>

struct completeRoots roots(float);

struct complexnumber{
       float R;
       float I;
   };

struct completeRoots{
    struct complexnumber root1;
    struct complexnumber root2;
};


void main(void){
    float x = -10; //ax^2 + bx + c = 0 ----- x = -b +-sqrt(b^2 - 4ac)/ 2a
    struct completeRoots Roots;
    Roots = roots(x);
    
    printf("main: square root of %f is %.3f+i%f\n", x, Roots.root1.R, Roots.root1.I);
    printf("main: square root of %f is %.3f+i%f\n", x, Roots.root2.R, Roots.root2.I);
    
    system("pause");
}


struct completeRoots roots(float y) {
    
    struct completeRoots Rt;
    
    //convert negative number and sqrt
    if(y >= 0){
        Rt.root1.R = sqrt(y);
        Rt.root1.I = 0;
        Rt.root2.R = - sqrt(y);
        Rt.root2.I = 0;
    } else {
        y = -1 * y;
        Rt.root1.R = 0;
        Rt.root1.I = sqrt(y);
        Rt.root2.R = 0;
        Rt.root2.I = -1 * sqrt(y);
    }
    
    return(Rt);
}
*/


/*
 calculating the roots of quadratic equation is very important
 control systems / electrical systems
 DSP Processor
 2nd order transfer function :::
*/



//00:57:00 of lecture ** important 









