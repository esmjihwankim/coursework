#include "rti.h"

int scaler;
int i = 0;
int pin = 0x01;

// s : scaler by 0.5ms
// eg) s=2000 -> 0.5*2000 = 1s

/*************************************************/
/*  ¸®¾óÅ¸ÀÓ ÀÎÅÍ·´Æ®¸¦ ÃÊ±âÈ­ ÇÑ´Ù.*/
/*************************************************/
void init_rti(int s)
{
	scaler = s;
	Crg.rtictl.byte = 0b00010111;     //¸®¾óÅ¸ÀÓ ÀÎÅÍ·´Æ®ÀÇ ¼Óµµ °áÁ¤(0.5ms ·Î ÇÏ½Ã¿À) -> 8 x 2^10
	Crg.crgint.byte |= 0b10000000;		//¸®¾óÅ¸ÀÓ ÀÎÅÍ·´Æ® enable
	
}

/*************************************************/
/*  ¸®¾óÅ¸ÀÓ ÀÎÅÍ·´Æ®°¡ ¹ß»ıÇÒ ¶§¸¶´Ù */
/*  7-¼¼±×¸ÕÆ®°¡ µ¿ÀÛ. */
/*  ex) Pim.pth.byte = 0x01       ¼¼±×¸ÕÆ® °ªÃâ·Â*/
/*  ÀÚÀ¯·Ó°Ô ÄÚµùÀ» ÇÏ½Ã¿À.			*/
/*************************************************/
void rti_service(void) 
{
  
  if(scaler==1)  // SW2 Pressed  - Clockwise - Increase Port Number 
  {  
     if(Pim.pth.byte == 0b00100000) Pim.pth.byte = 0b00000001;   
     else Pim.pth.byte = Pim.pth.byte << 1;
                  
  } 
                                 
  else if(scaler==2)    // SW3 Pressed - Counter Clockwise - Decrease Port Number 
  {      
     if(Pim.pth.byte == 0b00000001) Pim.pth.byte = 0b00100000;   
     else Pim.pth.byte = Pim.pth.byte >> 1; 
   
  }
  
  else  // Scaler == 3 - Stop 
  {
      
  }
  
}

/*************************************************/
/*  ¸®¾óÅ¸ÀÓ ÀÎÅÍ·´Æ®°¡ ¹ß»ıÇÒ ¶§ÀÇ µ¿ÀÛÀ» Á¤ÀÇÇÑ´Ù. */
/*************************************************/

/* 0.5ÃÊ ¸¶´Ù rti_handler ½ÇÇ  */
void rti_handler(void)
{
	static int count = 0;   //static
	
	count++;

	if (count >= 2000) {
	 /*¾à 1ÃÊ¸¶´Ù ½ÇÇà*/
		// process task
		rti_service();
  	count = 0;

		
	}
	// clear flag
  Crg.crgflg.bit.rtif = 1;    // ½Ç½Ã°£ ÀÎÅÍ·´Æ® ÇÃ·¡±× ÃÊ±âÈ­

}
