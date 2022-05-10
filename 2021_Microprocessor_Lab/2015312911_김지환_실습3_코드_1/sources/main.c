#include "main.h"

void main ()
{  
  int_disable();                      //인터럽트 disable
  																		//리얼타임 인터럽트 초기화 
  ini_interrupt();			//인터럽트 초기화      (약 0.5ms마다 인터럽트)
  																	
  Regs.ddrb.byte = 0xFF;
  Regs.portb.byte = 0xFF;		
  
  int_enable();
      
	//Insert Application Software Here.
	for (;;); 

}