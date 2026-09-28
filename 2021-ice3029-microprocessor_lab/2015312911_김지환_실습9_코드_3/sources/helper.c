#include "helper.h"


/*
@brief functions to help value conversions
*/

// Mapping 0-1023 to 1-9
char convertADCLevel(int cnt)
{
 	//ATD 값을 0~9로 변환하는 프로그램을 작성하시오.
 	char mapping;
  	
  if(cnt >= 409 && cnt < 435) {     // maximum clockwise spin -> zero 
 	  mapping = '0';
 	} else if (cnt >= 435 && cnt < 487){
 	  mapping = '1';
 	} else if (cnt >= 487 && cnt < 513){
 	  mapping = '2';
 	} else if (cnt >= 513 && cnt < 565){
 	  mapping = '3';
 	}  else if (cnt >= 565 && cnt < 617){
 	  mapping = '4';
 	}  else if (cnt >= 617){
 	  mapping = '5';              // minimum clockwise spin 
 	} 

 	return mapping;	
}


void operateMotor(void) {
    char str[20];
    static int flag = 0;  
    static int speed = 0;
    if(flag==0) // incrase 
    {   
       speed++;
       if(speed==5){
          flag++; 
       }
    } 
    else if (flag==1) // decrase 
    {
       speed--;
       if(speed<0)flag++;
    } 
    else  // stop  
    { 
    }
    
    //write to LCD
    sprintf(str, "%d", speed);
    write_string(0x00, str);
    ms_delay(20);

    switch(speed) 
    {
        case 0:
          set_pwm(250, 0);
          break;
        case 1:
          set_pwm(250, 125);
          break;
        case 2:
          set_pwm(224, 112);
          break;
        case 3:
          set_pwm(200, 100);
          break;
        case 4:
          set_pwm(174, 87);
          break;
        case 5:
          set_pwm(150, 75);
          break;
    }
    ms_delay(50);
}




    


