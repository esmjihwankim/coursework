#include "main.h"
unsigned char RX[11]; 
/*RX[11]는 시리얼 통신 모듈과 컴퓨터 사이에 주고받을 문자를 저장하는 버퍼의 역할을 한다.  최대 받을 수 있는 문자열을 11개로 제한하였다.*/
void main ()
{  
  int_disable();
  init_sci0(19200,RX);    
/*시리얼 포트를 초기화 하는 역할이다. bps는 19200이고 문자열의 최대 길이는 10이다. */

  // 포트 B와 포트 M의 방향 설정
  Regs.ddrb.byte = 0b11111111;  // 포트 B는 모두 출력으로 설정
  Pim.ddrm.byte = 0b11000000;   // 포트 M의 6,7번 핀을 출력으로 설정
    
  // 모든 LED 꺼두기
  Regs.portb.byte = 0b11111111;   // 포트 B의 모든 핀을 1로 설정
  Pim.ptm.byte = 0b11000000;      // 포트 M의 6,7번 핀을 1로 설정 
  
  int_enable();
	write_sci0( "SCI OK" );   // 하이퍼터미널에 "SCI OK" 메시지 출력

  for (;;){ 
  }
}