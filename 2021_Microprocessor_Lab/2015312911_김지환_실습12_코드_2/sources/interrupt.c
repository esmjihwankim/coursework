#include "interrupt.h"


int num[16]; 
char binary_num[16];
int pos = 0;
int i;

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

// SW1 : convert binary to decimal and print to CAN 
void interruptX_function (void)    
{	  
     int res = 0; 
     write_can0(0, binary_num, pos+1);  
     ms_delay(20);
      
}


void interruptJ_function(void)
{
  char print_num[10] = {0x00, };
  // SW2 : select binary (between 0 and 1)
  if(Pim.pifj.byte & 0x01)     
  {  
      num[pos] = !num[pos];

      for(i = 0; i <= pos; i++) 
      {
          binary_num[i] = num[i] + '0';
          print_num[i] = binary_num[i];
      }     
      write_string(0x40, print_num);
      ms_delay(20);
       
      Pim.pifj.byte |= 0x01;    // 인터럽트 플래그 초기화 
  }
  // SW3 : move to next number 
  else if(Pim.pifj.byte & 0x02)  
  {  
      pos++;
      
      for(i = 0; i <= pos; i++) 
      {
          binary_num[i] = num[i] + '0';
          print_num[i] = binary_num[i]; 
      }   
      write_string(0x40, print_num);  
      ms_delay(20);
      
      Pim.pifj.byte |= 0x02;   // 인터럽트 플래그 초기
  }
  
               
}