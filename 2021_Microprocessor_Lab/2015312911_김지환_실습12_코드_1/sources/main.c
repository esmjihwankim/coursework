#include "main.h"

#define MAX_STRING 15
 


char sci_rx_buffer[MAX_STRING+1];
char sci_tx_buffer[MAX_STRING*2];

char can0_rx_buffer[MAX_STRING+1];


void main ()
{
	
  int_disable();
  init_can0(can0_rx_buffer);	
  int_enable();	
		
  write_can0( 0, "CAN OK!", 7); 
 
	
	for (;;);
}