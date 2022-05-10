#include "interrupt.h"

/*************************************************/
/*  포트 J를 인터럽트로 사용하도록 설정한다.   */
/*************************************************/
void ini_interrupt(void)
{
   Pim.ddrj.byte=0b00000000;    // 인터럽트 포트의 방향 결정
   Pim.piej.byte=0xff;		// 인터럽트 포트의 인터럽트 enable
   Pim.ppsj.byte=0x00;		// 인터럽트 포트의 엣지 설정  
}

/*****************************************************/
/*  스위치 2,3에 연결된 포트 J의 동작을 설정한다.	*/
/*  스위치 2는 시계방향으로 회전                 	 */
/*  스위치 3은 반시계방향으로 회전.              */
/*  스위치 1은 정지			               */
/*****************************************************/

// SW1
void interruptX_function (void)    
{	  
    int i, j;
    if(g_queue.rear->data != 1) queuePush(&g_queue, 1);
    queueDisplay(&g_queue);
    for (i = 0; i < 100; i++) {
        for (j=0; j < 2650; j++);     // 아무것도 하지 않으면서 시간 지연
    }
}


void interruptJ_function(void)
{
  // SW2
  if(Pim.pifj.byte & 0x01)     
  { 
      if(g_queue.rear->data != 2) queuePush(&g_queue, 2);  
      Pim.pifj.byte |= 0x01;    // 인터럽트 플래그 초기화 
  }
  // SW3 
  else if(Pim.pifj.byte & 0x02)  
  {  
      if(g_queue.rear->data != 3) queuePush(&g_queue, 3);
      Pim.pifj.byte |= 0x02;   // 인터럽트 플래그 초기
  }
  
  queueDisplay(&g_queue);
               
}