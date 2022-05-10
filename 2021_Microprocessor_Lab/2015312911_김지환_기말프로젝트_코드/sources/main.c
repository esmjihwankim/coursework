#include "main.h"

unsigned char RX[11]; 

void main ()
{
    
    // initialize variables
    int next_floor, diff;
    g_current_floor = 1;
    g_operation_flag = 0; 
    queueCreate(&g_queue);
    queueCreate(&g_history_queue);

    init_atd0();
    int_disable();                     
    // initiate interrupt 																
    ini_interrupt();	
			
    init_pwm();
    init_LCD();
    
    init_sci0(19200, RX);

    // enable interrupt 																	
    int_enable();			
    xint_enable();
               
    // LED
    Regs.ddrb.byte = 0xFF;
    Regs.portb.byte = 0x00;
    Pim.ddrm.byte = 0b11000000;
    Pim.ptm.byte = 0b00000000;
    
    // 7 Segment                         
    Pim.ddrh.byte= 0xFF; 
    print_7seg_number(g_current_floor);
    
    // Buzzer 
    Regs.ddra.byte |= DDRA7;
    Regs.porta.byte |= PTA7;
    
    p_buffer = p_base_buffer;
    write_sci0("\r\rELEVATOR::SCIOK\r");
    ms_delay(20);

    
  	//Insert Application Software Here.
  	for (;;) 
  	{
  	   // LCD 
  	   showADCLevelOnLCD(); 
  	   
  	   // Serial data parsing and actions
  	   if(dataCompleteSignal == 1) {
  	      parse(p_buffer);
  	      dataCompleteSignal = 0;
  	   }
  	   
  	   // Queue Operation 
  	   if(!queueIsEmpty(&g_queue) && g_operation_flag == 0) 
  	   {
  	      next_floor = queuePop(&g_queue);
  	      queuePush(&g_history_queue, next_floor);
  	      
  	      if(g_history_queue.nodeCount > 10) 
  	         queuePop(&g_history_queue);
  	      
  	      queueDisplay(&g_queue);
          ms_delay(20);
  	      diff = next_floor - g_current_floor;
  	      if(diff == 0) openCloseDoor();
  	      else 
  	      {
  	          write_sci0("\r--Start--\r");
  	          ms_delay(20);
  	          g_operation_flag = 1;
  	          operate(diff);
  	          g_current_floor = next_floor; 
  	      }
  	      
  	   }  
  	      
  	} 
  	

}