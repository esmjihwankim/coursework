//
//  recursion.c
//  PracticeSession9
//
//  Created by Jihwan Kim on 2020/05/30.
//  Copyright © 2020 LogicLead. All rights reserved.
//

//#include <stdio.h>
//
//
//void printCombination(int arr[], int n, int r);
//
//void combinationUtil(int arr[], int data[], int start, int end, int index, int r);
//
//
//
//int main(){
//
//    int arr[] = {1, 2, 3, 4, 5};
//    int r = 3;
//    int n = sizeof(arr)/sizeof(arr[0]);
//    printCombination(arr, n, r);
//
//}
//
//
//void printCombination(int arr[], int n, int r){
//
//      //A temporary array to store all combination one by one
//      int data[r];
//
//      //Print all combination using temporary array
//      combinationUtil(arr, data, 0, n-1, 0, r);
//
//
//}
//
//
//void combinationUtil(int arr[], int data[], int start, int end, int index, int r){
//
//    //current combination is ready to be printed, print it
//    if(index == r) {
//        for(int j = 0; j < r; j++){
//            printf("%d ", data[j]);
//        }
//        printf("\n");
//        return;
//    }
//
//    //replace index with all possible elements
//    for(int i = start; i <=end && end-i+1 >= r-index; i++){
//        data[index] = arr[i];
//        combinationUtil(arr, data, i+1, end, index+1, r);
//    }
//
//}
