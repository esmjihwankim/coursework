#include "elevator.h"



void operate(int floor) 
{
    static int flag = 0;  
    static int speed = 0;
    int dist = floor;
    
    // check negative 
    if(dist > 0) Pwm.pwmpol.byte = PPOL1 + PPOL2;
    else 
    {
        Pwm.pwmpol.byte = PPOL1 + PPOL3;
    }
    // set 7 segment before spinning 
    Pim.pth.byte = 0b00000001;

    write_sci0("\r--MOVING...--\r");
    ms_delay(20);
    // operate motor based on dist
    init_rti(dist); 
    
    return;     
}
     
     
     
void move(int time) 
{
    static int flag = 0;  
    static int speed = 0;
    static int max_cnt = 0;
    
    // incrase speed 
    if(flag==0) 
    {   
       speed++;
       if(speed==3) flag++; 
       
    }
    // maintain maximum speed 
    else if(flag == 1)
    {
       max_cnt++;
       if(max_cnt > time) flag++;
    }
    // decrase speed
    else if (flag==2) 
    {
       speed--;
       if(speed==0)flag++;
    }
    // stop when flag == 2  
    else  
    {
       init_rti(0); 
       flag = 0;
       max_cnt = 0;
       
       write_sci0("\r--STOP--\r");
       ms_delay(20);
       
       // open and close door
       print_7seg_number(g_current_floor);
       //write_sci0("\r--STOP--\r");
       //ms_delay(20);
       openCloseDoor();
       

       // end of movement operation 
       g_operation_flag = 0;
       
    }

    switch(speed) 
    {
        case 0: // stopped state 
          set_pwm(250, 0);
          break;
        case 1: // slowest 
          set_pwm(g_converted_adc+30, (g_converted_adc+30)/2);
          break;
        case 2:
          set_pwm(g_converted_adc+20, (g_converted_adc+20)/2);
          break;
        case 3:
          set_pwm(g_converted_adc+10, (g_converted_adc+10)/2);
          break;
    } 
     
}