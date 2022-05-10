#ifndef INTERRUPT_H        /*prevent duplicated includes*/
#define INTERRUPT_H
#define xint_enable() {asm andcc #0xBF;}

/*Includes*/
#include "projectglobals.h"
#include "lcd.h"
#include "sci.h"
#include "helper.h"
#include "atd.h"
#include "7segment.h"



void ini_interrupt(void);
void interruptJ_function(void);
void interruptX_function(void);  

#endif 
