/*====*====*====*====*====*====*====*====*====*====*====*====*====*====*====*

		                                 PWM 실습 1


1. GENERAL DESCRIPTION : 3일차 PWM 예제 
2. GENERAL ENVIRONMENT : Window XP / Metrowerks CodeWarrior 3.1 ( Target Board )
3. DEVELOPMENT NOTE
   1) Development Environment : Window XP / MC9S12DP256 Board
   2) Development Tool : Metrowerks CodeWarrior 3.1 ( Target Board )
   3) Edito : Metrowerks CodeWarrior 3.1 ( Target Board )
   4) Target MCU : MC9S12DP256 (16bit)
   
4. Project Description: 모터 시계 방향으로 구동

5. HISTORY 
   /*****************************************************************************/
   /*YYYY-MM-DD   Version        Name                   Description             */
   /*2008-10-18     1.0      Automation Lab             PWM 실습1                 */
   /*****************************************************************************

6. REFERENCES : Copyright(c) 1994-2008 Automation Lab. All Rights Reserved.

*====*====*=====*====*====*====*====*====*====*====*====*====*====*====*====*/

#include <stdlib.h>
#include "main.h"
#include "projectglobals.h"                                  
                   
void main ()
{
  int i;
  int cnt, adc;
  char scaled_adc;
  char str[10]; 
  
  init_atd0();          
  init_pwm();  // enable PWM channel 
  init_LCD();  // debug with LCD 
  
  	
  while(1) 
  {
    adc = get_atd0(0); 
    scaled_adc = convertADCLevel(adc); 
    
    // ADC=0 in Max Clockwise Direction 
    sprintf(str, "%c", scaled_adc);
    write_string(0x00, str);
    ms_delay(20);
    scaled_adc -= '0';
    
    switch(scaled_adc) {
      case 0:
        set_pwm(250, 0);
        break;
      case 1:
        set_pwm(250, 125);
        break;
      case 2:
        set_pwm(224, 112);
        break;
      case 3:
        set_pwm(200, 100);
        break;
      case 4:
        set_pwm(174, 87);
        break;
      case 5:
        set_pwm(150, 75);
        break;
    }
    ms_delay(50);
  }
  
  
  

}


