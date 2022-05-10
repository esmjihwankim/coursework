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

 
         
                







    


