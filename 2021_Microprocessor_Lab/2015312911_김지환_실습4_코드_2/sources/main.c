#include "main.h"
#include <stdio.h>

void main ()
{
    init_LCD();         // LCD를 사용하기 위한 초기화
    int_disable(); 
    ini_interrupt();
    xint_enable();
    int_enable();                             
    
    
    write_string(0x00, "NUM1=");   //LCD에 초기화면 표시
    write_string(0x08, "NUM2="); 
    
    for( ; ; );
}
