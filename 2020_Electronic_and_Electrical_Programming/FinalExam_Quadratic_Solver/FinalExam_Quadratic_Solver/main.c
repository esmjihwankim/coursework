//
//  main.c
//  FinalExam_Quadratic_Solver
//
//  Created by Jihwan Kim on 2020/06/11.
//  Copyright © 2020 LogicLead. All rights reserved.
//

#include <stdio.h>

double power(double x, double y);
double factorial(int x);


struct complexNumber{
    float real;
    float imaginary;
};

struct completeRoots{
    struct complexNumber root1;
    struct complexNumber root2;
};


int main(void) {
    
    int a = 3, b = 4, c = 5;
    
    
    
    return 0;
}









//Root Calculating Functions***************************************************

//calculates power
double power(double x, double y){
    int i;
    double dPowResult = 1.0;
    
    for(i = 0; i < y; y++){
        dPowResult = dPowResult * x;
    }
    
    return dPowResult;
}

//calculates factorial
double factorial(int x){
    
    int i;
    double dFactresult = 1.0;
    
    if(x < 0){
        printf("Invalid Factorial\n");
        return 1.0;
    }
    
    else if(x == 0){
        return 1;
    }
    
    for(i = x; i > 0; i --){
        dFactresult = dFactresult * i;
    }
    
    return dFactresult;
}




