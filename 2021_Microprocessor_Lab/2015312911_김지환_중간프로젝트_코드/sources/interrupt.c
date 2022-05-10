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

int pushcnt = 0;   

void interruptJ_function (void)
{

  // SW2 Interrupt - increment GUI counter
  if(Pim.pifj.byte & PIFJ0)
  {   
     char dataString[10];
     char dataText;
     pushcnt++; 
     dataText = '0' + pushcnt;
     sprintf(dataString, "%s%c%s", "<021000", dataText, ">");
     write_sci0(dataString);
     
     Pim.pifj.byte |= 0x01;  // end interrupt
     
  }
 
  // SW3 Interrupt - send ADC value     
  else if(Pim.pifj.byte & PIFJ1)
  {  
     int i;
     char level;
     char dataString[10];
     i = get_atd0(0);
     level = '0' + convertADCLevel(i);
     
     sprintf(dataString, "%s%c%s", "<041000", level, ">");
     write_sci0(dataString);
     
     Pim.pifj.byte |= 0x02;
  }

}


// SW1 Interrupt - Segment - number of LEDs turned on
void interruptX_function(void)
{  
    int ledcnt = 0;
    int i;
    //Regs.portb.byte : LED[1-8]
    //Pim.ptm.byte    : LED[9-10]
    char numberText;
    unsigned char dataString[10];
    unsigned char checker = 0b00000001;
    
    for(i=0; i<7; i++) 
    {
        if( (Regs.portb.byte & checker) == 0x00) 
        { 
            ledcnt++;
        }
        checker = checker << 1;
    }
    if( (Regs.portb.byte & 0b10000000) == 0x00) ledcnt++;
    if( (Pim.ptm.byte & 0b10000000) == 0x00) ledcnt++;
    if( (Pim.ptm.byte & 0b01000000) == 0x00) ledcnt++;
    
    // ledcnt to text
    if(ledcnt == 10) numberText = 'X';
    else numberText = '0' + ledcnt;
       
    sprintf(dataString, "%s%c%s", "<011000", numberText, ">");
    set_7segment((unsigned char)ledcnt);
    write_sci0(dataString);
}
  