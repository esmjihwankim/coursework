//
//  main.c
//  PracticeSession9
//
//  Created by Jihwan Kim on 2020/05/30.
//  Copyright © 2020 LogicLead. All rights reserved.
//

/*
 Approach :
 
 1. Find all the possible combimantions of chocolate obtaining method
 test case
 8 9 8 1 2      : 0th element chosen -> 8
 8 1 2          : 0th element cohsen -> 8
 2              :
 
 8 + 8 + 2 = 18
 
 when 9 is chosen at the start, the final value will be 9 + 2 = 11 which is wrong
 
 2. compare all simulated results and find maximum of the array
*/



#include <stdio.h>
#include <stdlib.h>
//Functions
void findMax(int* bagsArray, int n);
void maxUtility (int* bagsArray, int* iaValueMemo, int iMemoIndex, int iaUnavailableCell[100], int chosenIndex, int n);

//Global Variable
int giaMyBag[100] = {0};
int giaCaseSum[100] = {0};
int giaCaseSumIndex = 0;

int main() {

    int n, i, j;
    int* indexMemo;
    int* ipChocolateBag;

    printf("Input the number of bags?\n");
    scanf("%d", &n);

    //allocate memory
    indexMemo = (int*)malloc(sizeof(int) * n);
    ipChocolateBag = (int*)malloc(sizeof(int) * n);

    //input the number of chocolates into the bag (global)
    printf("Input the bags array?\n");
    for(i = 0; i < n; i++){
        scanf("%d", &ipChocolateBag[i]);
    }
    
    //check the input value
    printf("current amount of chocolates in %d bags ::\n\n", n);
    for(i = 0; i < n; i++){
        printf("%d ", ipChocolateBag[i]);
    }
    printf("\n");
    
    
    //finding all possibilities of chocolate stealing ;)
    findMax(ipChocolateBag, n);
  
    
    //finding maximum from the global array
    //which has all simulated results
    int finalMaximum = 0;
    for(j = 0; j < giaCaseSumIndex; j++){
        if(giaCaseSum[j] > finalMaximum){
            finalMaximum = giaCaseSum[j];
        }
    }
    printf("\n\nThe Maximum number of chocolates that can be stolen is %d\n\n", finalMaximum);
    
    return 0;
}

//simulates all the stealing methods. all variables and arrays initialized in this function
void findMax(int* ipBagsArray, int n){
    int i, j;
    
    int* iaValueMemo = (int*)malloc(sizeof(int) * n);
    int* iaUnavailableCell = (int*)malloc(sizeof(int) * n);
    int iMemoIndex = 0;
    
    
    //initialize array
    for(i = 0; i < n; i++){
        iaValueMemo[i] = 0;
        iaUnavailableCell[i] = 0;
    }
    
    
    //loop through all first choice // chosen index = i
    for(i = 0; i < n; i++){
        maxUtility(ipBagsArray, iaValueMemo, iMemoIndex, iaUnavailableCell, i, n);
        
        //set the values to initial state
        for(j = 0; j < n; j++){
            iaValueMemo[j] = 0;
            iaUnavailableCell[j] = 0;
        }
        iMemoIndex = 0;
    }

}

//recursion to find all of the chocolate stealings
void maxUtility (int* bagsArray, int* iaValueMemo, int iMemoIndex, int iaUnavailableCell[100], int chosenIndex, int n){
    
    int i, j, k;
    
    //1. record the picked value
    iaValueMemo[iMemoIndex++] = bagsArray[chosenIndex];

    //2. disable adjacent cells
    iaUnavailableCell[chosenIndex] = 1;
    
    if((chosenIndex - 1) >= 0){
        iaUnavailableCell[chosenIndex - 1] = 1;
    }
    if(chosenIndex + 1 < n){
        iaUnavailableCell[chosenIndex + 1] = 1;
    }

    
    //#100 Test Output
    printf("#100 iaUnavailableCell::");
    for(i = 0; i < n; i++){
        printf("%d ", iaUnavailableCell[i]);
    }
    printf("\n");
    
    
    //recurse where array is available // chosen index = i
    int possibleBagFlag = 0;
    for(i = 0; i < n; i++){
        if(iaUnavailableCell[i] == 0){
            maxUtility(bagsArray, iaValueMemo, iMemoIndex, iaUnavailableCell, i, n);
            possibleBagFlag = 1;
        }
    }
    
    //no more possible chocolate bag exists
    //add all the chocolate from individual bags possible
    if(possibleBagFlag == 0){
        int tmpSum = 0;
        for(j = 0; j < n; j++){
            tmpSum += iaValueMemo[j];
        }
        giaCaseSum[giaCaseSumIndex] = tmpSum;
        
        iaValueMemo = NULL;
        free(iaValueMemo);
        iMemoIndex = 0;
        
        printf("with giaCase Sum = %d, Case ended\n", giaCaseSum[giaCaseSumIndex]);
        giaCaseSumIndex++;
        return;
    }
}

