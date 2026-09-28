#include "sci_polling.h"


void __init_sci0(int baud_rate) //, char *rxbuf, int rx_max) 
{

  unsigned long oscclk, busclk;
  unsigned short bd;

	oscclk = 16000000;						// Set Oscillator Freq. = 16 MHz
  busclk = oscclk/2;					// Set Bus Freq. = (1/2) * Oscillator Freq.

  bd = (unsigned short)((busclk / 16) / baud_rate);   
  Sci0.scibd.word = bd;  
  
  Sci0.scicr1.byte = 0x0;
  Sci0.scicr2.byte = TE + RE;

	//txoffset_sci0 = 0;
	//rxbuffer_sci0 = rxbuf;
	//rxoffset_sci0 = rx_max;

  return;
}


void __write_sci0(char *buf, int length)
{
  for (; length > 0; length--) {
    
    while ((Sci0.scisr1.byte & 0x80) == 0)
      ;  
    
    if (*buf == 0x0d)
      Sci0.scidrl.byte = 0x0a;
    
    if (*buf == '$') {
      Sci0.scidrl.byte = *buf;
      break;
    }
    
    Sci0.scidrl.byte = *buf++;
  }
}


int __read_sci0(char *buf, int max) 
{

  int i = 0;

  unsigned char rc;
  
  for ( ; max > 0; max--) {
    while ( (Sci0.scisr1.byte & RDRF) == 0) 
      continue;
      
	 	rc = Sci0.scidrl.byte; /* data read */

		buf[i] = rc;
		i++;
		
		if (rc == '$') {
		  return i;
		}
		
	} /* end of for() */

  buf[i-1] = '$';
	 
	return i;
}




