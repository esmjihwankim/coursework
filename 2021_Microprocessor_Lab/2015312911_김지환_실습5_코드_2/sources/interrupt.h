#ifndef INTERRUPT_H
#define INTERRUPT_H
#include "projectglobals.h"
#define xint_enable() { asm andcc  #0xBF; }

void ini_interrupt(void);
void interruptJ_function(void);

#endif