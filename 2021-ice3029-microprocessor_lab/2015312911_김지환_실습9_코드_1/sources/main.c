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
  char p = 250;
  char d = 250 / 2;
  init_pwm();  
  	
  while(1) 
  {      
    set_pwm(p,d);  	
  }

}
