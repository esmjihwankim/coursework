#ifndef HELPER_H
#define HELPER_H

#include "sci.h"
#include "stdio.h"

int txtdecToDecimal(char* data_text);
int txthexToDecimal(char* data_text);
int txtbinToDecimal(char* data_text);

char convertADCLevel(int cnt);


void showError(int errCode);


int findError(int group_number, int cmd_class, 
              int cmd_number, int data_format, 
              int data_cnt);
              

#endif /* HELPER_H */