#include "rti.h"

int time, stage = 0, negative_flag = 0;
int i = 0;
int pin = 0x01;


void init_rti(int t)
{
    if(t < 0) 
    {
      time = -t;  // time taken
      negative_flag = 1;
    }
    else 
    {
      time = t;
      negative_flag = 0;
    }
    stage = 0;
    Crg.rtictl.byte = 0b00010111;     //리얼타임 인터럽트의 속도 결정(0.5ms 로 하시오) -> 8 x 2^10
    Crg.crgint.byte |= 0b10000000;		//리얼타임 인터럽트 enable
}


/* 
@brief determines the duration of motor movement
*/
void rti_service(void) 
{
   if(time==0) return;
   
   // motor movement timing
   if(stage<3*time)
   {
      move(time);   
      stage++;
   } 
   else if (stage>=3*time && stage<4*time) 
   {
      // max pwm for some time
      stage++;
   } 
   else 
   {
      move(time);     
   }
 
}


/*
@brief called by interrupt vector table
*/
void rti_handler(void)
{
  	static int count = 0;   //static
    static int lcd_pos = 0;
  	
  	int adc_val;
  	
  	// read adc value real time (adc value is global) 
  	adc_val = get_atd0(0);
  	g_converted_adc = convertADCLevel(adc_val);
  	
  	
  	/*약 1초마다 실행*/
  	if (count >= 2000) 
  	{
  	  // g_operation_flag decides
  	  if(g_operation_flag == 0) lcd_pos = 0; 
  	  if(g_operation_flag == 1) 
  	  {
  	      if(negative_flag == 0) spin7SegmentClockwise();
  	      else if (negative_flag == 1) spin7SegmentAntiClockwise();
  	      
  	      if(lcd_pos > 11) lcd_pos = 0;
  	      showBufferingOnLCD(&lcd_pos); 
  	      lcd_pos++;
  	      
  	      rti_service();
  	  } 
  	  else lcd_pos = 0;
    	count = 0;
  	}
  	
  	count++;

  	
  	// clear flag
    Crg.crgflg.bit.rtif = 1;    // 실시간 인터럽트 플래그 초기화
    
}
