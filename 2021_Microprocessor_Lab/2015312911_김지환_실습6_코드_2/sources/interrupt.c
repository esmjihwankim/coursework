#include "interrupt.h"
#include <stdio.h>


/*************************************************/
/*  포트 J를 인터럽트로 사용하도록 설정한다. */
/*************************************************/
void ini_interrupt(void){
 
   Pim.ptj.byte = 0b00000000;    // 인터럽트 포트의 방향 결정
   Pim.piej.byte= 0xFF;		// 인터럽트 포트의 인터럽트 enable
   Pim.ppsj.byte= 0x00;		// 인터럽트 포트의 엣지 설정
 
}

/*****************************************************/
/*  스위치 2,3에 연결된 포트 J의 동작을 설정한다.    */
/*  스위치 2를 누르면 cnt 숫자가 증가하고 LCD에 표시한다.*/
/*  스위치 3을 누르면 cnt 숫자가 감소하고 LCD에 표시한다.  */
/*  스위치 1을 누르면 cnt값을 세크먼트 표시한다.     */
/*****************************************************/

int cnt1 = 0;
char alphabet = 'A';
int position = 0;      

char str1[8]=""; // 문자열 저장
char str2[8]="";  
char str3[16]="";

void interruptJ_function (void){

  // SW2의 인터럽트 발생 - choose alphabet 
  if(Pim.pifj.byte & PIFJ0)  {   
 
    alphabet++;
    
    //check character
    if( (alphabet > 'Z') && (alphabet < 'a') ) 
        alphabet = 'a';
    if(alphabet > 'z') 
        alphabet = 'A';
    
    str1[position] = alphabet;
    write_string(0x00, str1);
    Pim.pifj.byte |= 0x01;                         
  }
 
  // SW3의 인터럽트 발생 - next cursor   
  else if(Pim.pifj.byte & PIFJ1)  {  
     if(alphabet == 'A'-1) alphabet = 'A'; 
     str1[position] = alphabet; 
    
     position++;
     alphabet = 'A'-1;
     Pim.pifj.byte |= 0x02;
     str1[8] = "";
  }
  
  
}


// switch 1 - send to sci 
void interruptX_function(void){  
    	write_sci0( (unsigned char*) str1);
}
  