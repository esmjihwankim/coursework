#include "main.h"

void delay(unsigned int n);

void main()
{   
    //unsigned char mask;

    
    // 포트 B 입출력방향 설정
    Regs.ddrb.byte = 0b11111111;    // 포트 B를 모두 출력으로 설정
    
    // 모든 LED 꺼두기
    Regs.portb.byte = 0b11111111;   // 포트 B의 모든 핀을 1로 설정    
    
        
    for (;;) {      
    
        
        Regs.portb.byte = 0b01111110;
     
        delay(5);
        
        Regs.portb.byte = 0b10111101;
        
        delay(5);
        
        Regs.portb.byte = 0b11011011;
        
        delay(5);
        
        Regs.portb.byte = 0b11100111;
        
        delay(5);
        
        Regs.portb.byte = 0b11111111;
         
        delay(5);
        
        Regs.portb.byte = 0b11011011;
        
        delay(5);

        Regs.portb.byte = 0b10111101;      
        
        delay(5);                         
    }
}

// 일정한 시간을 지연시키는 함수
void delay(unsigned int n) 
{
    unsigned int i;
    
    while (n > 0) {
        for (i=1; i != 0; i++);     // 아무것도 하지 않으면서 시간 지연
        n--;
    }
}




