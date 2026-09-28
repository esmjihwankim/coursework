#ifndef SCI_POLLING_H        /*prevent duplicated includes*/
#define SCI_POLLING_H


/*Includes*/
#include "projectglobals.h"

void __init_sci0(int baud_rate); //, char *, int);

int __read_sci0(char *buf, int max);

void __write_sci0(char *test, int length);

#endif /*SCI_H*/