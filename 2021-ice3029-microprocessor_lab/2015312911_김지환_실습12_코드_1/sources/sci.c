#include <stdio.h>
#include <string.h>
#include "sci.h"
#include "mscan.h"


static char *txbuffer_sci0;
static int txoffset_sci0;

static char *rxbuffer_sci0;
static int rxoffset_sci0;


 
void init_sci0(int baud_rate, char *rxbuf, int rx_max) 
{

  unsigned long oscclk, busclk;
  unsigned short bd;

	oscclk = 16000000;						// Set Oscillator Freq. = 16 MHz
  busclk = oscclk/2;					// Set Bus Freq. = (1/2) * Oscillator Freq.

  bd = (unsigned short)((busclk / 16) / baud_rate);   
  Sci0.scibd.word = bd;  
  
  Sci0.scicr1.byte = 0x0;
  Sci0.scicr2.byte = TE + RE + RIE;          /* enable both the transmitter & receiver */ 

	txoffset_sci0 = 0;
	rxbuffer_sci0 = rxbuf;
	rxoffset_sci0 = rx_max;

  return;
}


void write_sci0(char *text, int length)
{
	txbuffer_sci0 = text;
	txoffset_sci0 = length;
	Sci0.scicr2.byte += TIE;
	
}


void sci0_handler(void)
{
  static unsigned char i=0; /* index into command */
	static int j = 0; // index of transmition buffer
	unsigned char status;
  unsigned char rc;
  
	status = Sci0.scisr1.byte;
	
	if ( (status & RDRF) != 0) {
	 	rc = Sci0.scidrl.byte; /* data read */

		rxbuffer_sci0[i] = rc;
		i++;
		
		if (rc == '$') {		  
		
			__write_sci0(rxbuffer_sci0, i);
			
		  
		  i = 0;
		  		
			
		}
	} /* end of "if ( (status & RDRF) != 0) {" */
	
	// ready to transmit a data
	if ( (status & TDRE) != 0) {
		if (j >= txoffset_sci0) {
			Sci0.scicr2.byte = Sci0.scicr2.byte & ~TIE; // mask interrupt
			txoffset_sci0 = 0;
			j = 0; // clear index
		} else {
			Sci0.scidrl.byte = txbuffer_sci0[j]; // send a data
			j++; // increase index
		} /* end of "if (j >= txoffset_sci0) {" */
	} /* end of "if ( (status & TDRE) != 0) {" */
	
	return;
  
}