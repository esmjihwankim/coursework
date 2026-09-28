#include "7segment.h"

void init_7segment(void) 
{
   Pim.ddrh.byte = 0xFF;  
}


void print_7seg_number(int number) 
{
 
 switch(number) 
 {
 
  case 0:
      Pim.pth.byte = 0b00111111;
      break;
 
  case 1:
      Pim.pth.byte = 0b00000110;
      break;
                                                          
  case 2:
      Pim.pth.byte = 0b01011011;      
      break;
  
  case 3:
      Pim.pth.byte = 0b01001111;      
      break;
  
  case 4:
      Pim.pth.byte = 0b01100110;      
      break;
  
  case 5:
      Pim.pth.byte = 0b01101101;      
      break;
  
  case 6:
      Pim.pth.byte = 0b01111100;      
      break;
  
  case 7:
      Pim.pth.byte = 0b00000111;      
      break;
  
  case 8:
      Pim.pth.byte = 0b01111111;      
      break;
  
  case 9:
      Pim.pth.byte = 0b01100111;      
      break;
  
  default:
      //Wrong Value
      break;
 }
 
 
}
