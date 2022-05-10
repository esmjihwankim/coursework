#ifndef SCI_H        /*prevent duplicated includes*/
#define SCI_H


/*Includes*/
#include "projectglobals.h"

#include "sci_polling.h"


void init_sci0(int, char *, int);
void write_sci0( char *text, int length);
void sci0_handler(void);



#endif /*SCI_H*/