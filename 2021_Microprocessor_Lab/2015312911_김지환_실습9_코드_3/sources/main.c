#include "main.h"


void main ()
{
  char str[20];  
  int_disable();                      //인터럽트 disable
  																		//리얼타임 인터럽트 초기화 
  init_rti(2000);				
  ini_interrupt();			//인터럽트 초기화      (약 0.5ms마다 인터럽트)
  init_pwm();
  init_LCD();
  																	
  int_enable();				//인터럽트 enable
  xint_enable();			
                
  Pim.ddrh.byte= 0xFF; 
  Pim.pth.byte = 0b00000001;
    
	//Insert Application Software Here.
	for (;;) { 
	    
	} 

}