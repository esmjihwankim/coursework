#ifndef SCI_H        /*prevent duplicated includes*/
#define SCI_H


/*Includes*/
#include "projectglobals.h"


void init_sci0(int, unsigned char *);
void write_sci0(unsigned char *text);
void sci0_handler(void);



#endif /*SCI_H*/