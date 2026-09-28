#include "helper.h"


/*
@brief functions to help value conversions
*/

// decimal is D4 
int txtdecToDecimal(char* data_text)
{
    int i;
    int result = 0;
    for(i = 0; i <= 3; i++)
    {
        result += (data_text[i]-'0');
        result *= 10; 
    }
    result /= 10;

    return result;
}

// Hex is D3
int txthexToDecimal(char* data_text)
{
    int i; 
    int result = 0;
    for(i = 0; i <= 2; i++)
    {
        // number between 0 - 9
        if(data_text[i] >= '0' && data_text[i] <= '9')
        {
            result += (data_text[i]-'0');
            result *= 16;
        }
        // A - F 
        if(data_text[i] >= 'A' && data_text[i] <= 'F')
        {
            result += (data_text[i] - ('A' - 1) + 9);
            result *= 16;
        } 
    }
    result /= 16; 
    return result;
}

// Binary is D10
int txtbinToDecimal(char* data_text)
{
    int i;
    int result = 0;
    for(i = 0; i <= 9; i++)
    {
        int tmp = (data_text[i] - '0');
        result += tmp;
        result *= 2;
    }
    result /= 2;
    return result;
}


// Mapping 0-1023 to 1-9
char convertADCLevel(int cnt)
{
 	//ATD 값을 0~9로 변환하는 프로그램을 작성하시오.
 	char mapping;
 	
  if(cnt >= 409 && cnt < 435) {
 	  mapping = 0;
 	} else if (cnt >= 435 && cnt < 461) {
 	  mapping = 1;
 	} else if (cnt >= 461 && cnt < 487){
 	  mapping = 2;
 	} else if (cnt >= 487 && cnt < 513){
 	  mapping = 3;
 	} else if (cnt >= 513 && cnt < 539){
 	  mapping = 4;
 	}  else if (cnt >= 539 && cnt < 565){
 	  mapping = 5;
 	}  else if (cnt >= 565 && cnt < 591){
 	  mapping = 6;
 	}  else if (cnt >= 591 && cnt < 617){
 	  mapping = 7;
 	}  else if (cnt >= 617 && cnt < 643){
 	  mapping = 8;
 	} else if (cnt >= 643){
 	  mapping = 9;
 	} 

 	return mapping;	
}



void showError(int error_type) 
{
    char dataString[10];
    char error_code = '0'+ error_type;
    
    sprintf(dataString, "%s%c%s", "<051000", error_code, ">");    
    write_sci0(dataString);
    
    return;
}


int findError(int group_number, int cmd_class,
              int cmd_number, int data_format, int data_cnt)
{
    
    int error_type = -1;
    
    // ERROR0&1:OverDataSize&LossDataSize 
    switch(data_format)
    {
      case 0: // 1 byte 
        if(data_cnt > 1) error_type = 0;
        else if(data_cnt < 1) error_type = 1;
        break;
      case 2: // 3 byte 
        if(data_cnt > 3) error_type = 0;
        else if(data_cnt < 3) error_type = 1;
        break;
      case 3: // 4 bytes
        if(data_cnt > 4) error_type = 0;
        else if(data_cnt < 4) error_type = 1;
        break;
      case 4: // 10 bytes 
        if(data_cnt > 10) error_type = 0;
        else if(data_cnt < 10) error_type = 1;
        break;
      case 5: // 16 bytes 
        if(data_cnt < 16) error_type = 0;
        else if(data_cnt > 16) error_type = 1;
        break;
      default: // ERROR4:OverFormatCnt
        error_type = 4;
        break;
    }
    
    // throw error and return error state
    if(error_type != -1)
    {
        showError(error_type);
        return -1;
    }
          
    // ERROR2:OverGroupCnt
    if(group_number < 0 || group_number > 5) 
        error_type = 2;
    // ERROR3:OverClassCnt
    else if(cmd_class < 0 || cmd_class > 1)
        error_type = 3;
    // ERROR5:CantFindCmd_LED
    else if(group_number == 0 && (cmd_number < 0 || cmd_number > 4))
        error_type = 5;
    // ERROR6:CantFindCmd_LCD
    else if(group_number == 3 && (cmd_number < 0 || cmd_number > 1))
        error_type = 6;
    
    // throw error and return error state
    if(error_type != -1)
    {
        showError(error_type);
        return -1;
    }
    
    return 0; 
}
    
    
      


 
         
                







    


