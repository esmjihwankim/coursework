#include "helper.h"


/*
  @brief functions to help value conversions
*/
unsigned char convertADCLevel(int cnt)
{
   	unsigned char mapping;
    	
    if(cnt >= 409 && cnt < 487)
   	{
   	  mapping = 220;
   	} 
   	else if (cnt >= 487 && cnt < 550)
   	{
   	  mapping = 180;
   	} 
   	else if (cnt >= 550)
   	{
   	  mapping = 150;   // minimum clockwise spin 
   	} 

   	return mapping;	
}


/*
  @brief Rings buzzer, opens door then closes door
*/
void openCloseDoor(void) 
{
    // RING BUZZER
    Regs.porta.byte &= 0b01111111;
    ms_delay(50);
    Regs.porta.byte |= 0b10000000;

    // c denotes center 
    //port m   0 0 c c 0 0 0 0
    
    // open - expand 1's 
    Regs.portb.byte = 0b00110000;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
    Regs.portb.byte = 0b01111000;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
    Regs.portb.byte = 0b11111100;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
    Regs.portb.byte = 0b11111110;
    Pim.ptm.byte   = 0b01000000;
    ms_delay(50);
    Regs.portb.byte = 0b11111111;
    Pim.ptm.byte   = 0b11000000;
    ms_delay(50);
    
    
    // close - shrink 1's 
    Regs.portb.byte = 0b11111110;
    Pim.ptm.byte   = 0b01000000;
    ms_delay(50);
    Regs.portb.byte = 0b11111100;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
    Regs.portb.byte = 0b01111000;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
    Regs.portb.byte = 0b00110000;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
    Regs.portb.byte = 0b00000000;
    Pim.ptm.byte   = 0b00000000;
    ms_delay(50);
}


/*
  @brief LCD manipulation depending on ADC
  and buffering action when moving
*/
void showADCLevelOnLCD(void) 
{
    int adc_val;
    char* adc_str = malloc(sizeof(char) * 3);
    
    memset(adc_str, ' ', 3);
    adc_val = get_atd0(0);
    
    if(adc_val > 999) adc_val = 999;
    sprintf(adc_str, "%d", adc_val);
    
    write_string(0x40, adc_str);
    free(adc_str);
}

void showBufferingOnLCD(int* pos) 
{      
    
    char* buffer_str = malloc(sizeof(char) * 12);
    memset(buffer_str, ' ', 12);
    
    buffer_str[*pos++] = '*';
    
    write_string(0x44, buffer_str);    
    free(buffer_str);
}



/*
  @brief Parses incoming string through SCI communication
  and controls board
*/
void spin7SegmentClockwise(void) 
{
    if(Pim.pth.byte == 0b00100000) Pim.pth.byte = 0b00000001;   
  	else Pim.pth.byte = Pim.pth.byte << 1;
}

void spin7SegmentAntiClockwise(void)
{ 
    if(Pim.pth.byte == 0b00000001) Pim.pth.byte = 0b00100000;   
    else Pim.pth.byte = Pim.pth.byte >> 1; 
}




/*
  @brief Parses incoming string through SCI communication
  and controls board
*/
void parse(char* buffer) 
{
    // variables for parsing 
    int group_number = 0;
    int cmd_class = 0;
    int cmd_number = 0;
    int data_format = 0; 
    char* data_text = malloc(sizeof(char)*30); 
    char* output_text = malloc(sizeof(char)*30);
    char* temp_text = malloc(sizeof(char) * 15);
    
    int i;
    int data_cnt = 0;
    
    // variables for board control
    int ledcnt=0;
    unsigned char checker = 0b00000001;
    
    
    // read 2 bytes group number 
    group_number = group_number + (*buffer - '0') * 10;
    buffer++;
    group_number = group_number + (*buffer - '0');
    buffer++;
    // read 1 byte cmd class 
    cmd_class = *buffer - '0';
    buffer++;
    // read 2 byte cmd number
    cmd_number = cmd_number + (*buffer - '0') * 10;
    buffer++; 
    cmd_number = cmd_number + (*buffer - '0');
    buffer++;
    // read 1 byte data format 
    data_format = *buffer - '0'; 
    buffer++;
    
    // count data size and throw ERROR0 
    while(*buffer != '\0') 
    {
       data_cnt++;
       buffer++;
    }
    
    //write_string(0x00,debug_str); 
    
    buffer -= data_cnt;
    
  
    // parsing data bits based on data format   
  	switch (data_format)
  	{
    	case 0:  // d1 - 1 byte 
    		*(data_text) = *buffer;
    		break;
    	case 2:  // d3 - 3 bytes
    		for (i = 0; i < 3; i++)
    		{
    			data_text[i] = *buffer;
    			buffer++;
    		}
    		break;
    	case 3:  // d4 - 4 bytes  
    		for (i = 0; i < 4; i++)
    		{
    			data_text[i] = *buffer;
    			buffer++;
    		}
    		break;
    	case 4:  // d10 - 10 bytes 
    		for (i = 0; i < 10; i++)
    		{
    			data_text[i] = *buffer;
    			buffer++;
    		}
    		break;
    	case 5:  // d16 - 16 bytes 
    		for (i = 0; i < 16; i++)
    		{
    			data_text[i] = *buffer;
    			buffer++;
    		}
    		break;
    	default:
    		break;
  	}

  	
  	/* Start operation */
  	
  	 // LED
    if(group_number == 0)
    {
        //turn on led using GUI
        if(cmd_class == 0)
        { 
            openCloseDoor();
        }
        
        // send door status (number of leds on)  
        else if (cmd_class == 1) 
        {
            ledcnt = 0;
            
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
            sprintf(output_text, "%s%d%s", "<001002", ledcnt, ">");
            write_sci0(output_text);
            ms_delay(10);
        }
    }
    
    // Buzzer 
    else if(group_number == 1)
    {
        
        int num = 0;
        i = 0;
        while(i < 10) {
           num += data_text[i] - '0'; 
           num *= 10;
           i++; 
        }
        num /= 10;
        
        Regs.porta.byte &= 0b01111111;
        ms_delay(num);
        Regs.porta.byte |= 0b10000000;

    }
    
    
    // LCD
    else if(group_number == 2)
    {
        write_string(0x00, data_text);  
    } 
    
    // ADC 
    else if(group_number == 3) 
    {
        int adc_val;
        char* adc_str = malloc(sizeof(char) * 4);
        char* sci_str = malloc(sizeof(char) * 20);
        
        memset(adc_str, 0, 4);
        adc_val = get_atd0(0);
        
        if(adc_val > 999) adc_val = 999;
        sprintf(adc_str, "%d", adc_val);
        sprintf(sci_str, "%s%s%s", "<0310030", adc_str, ">");
        
        write_sci0(sci_str);
        
        free(adc_str);  
        free(sci_str); 
    }
    
    // Floor 
    else if (group_number == 4) 
    {
        const node_t* tempNode; 
        
        memset(temp_text, '0', 15); 

        // control 
        if(cmd_class == 0) 
        {
           queuePush(&g_queue, data_text[0] - '0');  
        }
        
        // update 
        else if (cmd_class == 1)
        {
          // update current floor to GUI
          if(cmd_number == 0) 
          {
             sprintf(output_text, "%s%d%s", "<041002", g_current_floor, ">");
             write_sci0(output_text);
          } 
          
          // send all values in queue
          else if (cmd_number == 1)
          {
             i = 0;
             tempNode = (&g_history_queue)->front;
             while(tempNode != NULL) 
             {
                if(i >= 15) break;
                temp_text[i++] = ( (tempNode -> data) + '0');
                tempNode = tempNode->nextNode;
             }
             sprintf(output_text, "%s%s%s", "<041015", temp_text, ">");
             write_sci0(output_text);
          }
          
        }
        
    }
    
    // end of parse function 
    free(data_text);
    free(output_text);	
    free(temp_text);
    return; 
}




void showError(int error_type) 
{
    char dataString[10];
    char error_code = '0'+ error_type;
    
    sprintf(dataString, "%s%d%s", "<051000", error_code, ">");    
    write_sci0(dataString);
    
    return;
}








    


