#include "rti.h"

int scaler;
int i = 0;
int pin = 0x01;

// s : scaler by 0.5ms
// eg) s=2000 -> 0.5*2000 = 1s

/*************************************************/
/*  ∏ÆæÛ≈∏¿” ¿Œ≈Õ∑¥∆Æ∏¶ √ ±‚»≠ «—¥Ÿ.*/
/*************************************************/
void init_rti(int s)
{
	scaler = s;
	Crg.rtictl.byte = 0b00010111;     //∏ÆæÛ≈∏¿” ¿Œ≈Õ∑¥∆Æ¿« º”µµ ∞·¡§(0.5ms ∑Œ «œΩ√ø¿) -> 8 x 2^10
	Crg.crgint.byte |= 0b10000000;		//∏ÆæÛ≈∏¿” ¿Œ≈Õ∑¥∆Æ enable
	
}

/*************************************************/
/*  ∏ÆæÛ≈∏¿” ¿Œ≈Õ∑¥∆Æ∞° πﬂª˝«“ ∂ß∏∂¥Ÿ */
/*************************************************/
void rti_service(void) 
{
   static int max_reached = 0;
   
   if(max_reached<5)
   {
      operateMotor();
      max_reached++;
   } 
   else if (max_reached>=5 && max_reached<10) 
   {
      // max pwm for some time 
      max_reached++;
   } 
   else 
   {
      operateMotor();      
   }
    
   
}

/*************************************************/
/*  ∏ÆæÛ≈∏¿” ¿Œ≈Õ∑¥∆Æ∞° πﬂª˝«“ ∂ß¿« µø¿€¿ª ¡§¿««—¥Ÿ. */
/*************************************************/

/* 0.5√  ∏∂¥Ÿ rti_handler Ω««  */
void rti_handler(void)
{
	static int count = 0;   //static
	count++;
	
	
	if (count >= scaler) {
	 /*æ‡ 1√ ∏∂¥Ÿ Ω««‡*/
		// process task
		rti_service();
  	count = 0;
	}
	// clear flag
  Crg.crgflg.bit.rtif = 1;    // Ω«Ω√∞£ ¿Œ≈Õ∑¥∆Æ «√∑°±◊ √ ±‚»≠

}
