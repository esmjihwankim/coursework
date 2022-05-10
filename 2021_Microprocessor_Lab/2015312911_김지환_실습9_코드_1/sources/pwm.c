#include "main.h"

/*
 * PWM0 -> A
 * PWM1 -> /A
 * PWM2 -> B
 * PWM3 -> /B
 *
 * PWM0, PWM1 ->  62.5kHz
 *
 * 버스 클럭 : 8MHz */


/**************************************************/
/*   PWM을 초기화한다.                                 */
/**************************************************/

void init_pwm(void) 
{
 
  Pwm.pwme.byte = PWME0 + PWME1 + PWME2 + PWME3;
  //Pwm.pwme.byte = (	) ;  // PWM의 모든 채널(0~3)을 비활성화 한다.
  
  //Pwm.pwmpol.byte = PPOL1 + PPOL2;  // 각 채널의 극성을 설정한다.
  Pwm.pwmpol.byte = PPOL1 + PPOL3;
  
  Pwm.pwmclk.byte = 0x0;  // 각 채널의 클럭(A,B)을 선택한다.
  
  Pwm.pwmprclk.byte = PCKA2+PCKA1+PCKA0+PCKB2+PCKB1;  // 각 채널의 Clock Prescale 을 설정한다.

  Pwm.pwmcae.byte = CAE2+CAE3;  // 중앙 정렬(Center Align)할 채널을 설정한다.
  
  // PWM control
  Pwm.pwmctl.byte = 0x0;
  
  // shutdown
  Pwm.pwmsdn.bit.pwm7en = 0;  
 
}


/**************************************************/
/*   PWM의 주기와 두티를 설정한다.                          */
/**************************************************/
 
void set_pwm(unsigned char p, unsigned char d) 
{

  // disable PWM channel
  //Pwm.pwme.byte = (	);
  
  // 각 채널의 주기를 설정한다.
  Pwm.pwmper[0].byte = (p	);
  Pwm.pwmper[1].byte = (p	);
  Pwm.pwmper[2].byte = (p	);
  Pwm.pwmper[3].byte = (p	);
  
  // 각 채널의 듀티를 설정한다.
  Pwm.pwmdty[0].byte = (d	);
  Pwm.pwmdty[1].byte = (d	);
  Pwm.pwmdty[2].byte = (d	);
  Pwm.pwmdty[3].byte = (d	);

 
  // PWM의 모든 채널(0~3)을 활성화 한다.
  //Pwm.pwme.byte = (	);
  
}
