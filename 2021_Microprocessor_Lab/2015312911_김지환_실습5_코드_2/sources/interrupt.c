#include "interrupt.h"


/* port j used for interrupt */

void ini_interrupt(void) {
    Pim.ptj.byte = 0b00000000;
    Pim.piej.byte = 0xff;
    Pim.ppsj.byte = 0x00;
    
}

void interruptJ_function(void){
    //SW3 interrupt
    global_mode = !global_mode;    
    Pim.pifj.byte |= 0x02;
    
   
}