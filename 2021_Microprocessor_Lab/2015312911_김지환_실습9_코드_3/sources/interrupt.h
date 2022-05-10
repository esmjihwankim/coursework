#ifndef INTERRUPT_H        /*prevent duplicated includes*/
#define INTERRUPT_H

/*Includes*/
#include "projectglobals.h"

#define xint_enable()  {asm andcc   #0xBF;}

void ini_interrupt(void);
void interruptJ_function(void);
void interruptX_function(void);
  

#endif 
