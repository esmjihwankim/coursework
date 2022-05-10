/******************************************************************************
*                                             COPYRIGHT (c) MOTOROLA 2003   
* FILE NAME: projectglobals.h                                        
*                                                                           
* PURPOSE: header file for project level defines global variables
*		   and includes module drivers.  							 
*                                                                           
* DESCRIPTION:  project setup (peripherals and drivers)        
*                                                                           
* NOTE: Modify this file to specify which maskset peripheral you are using by
*		uncommenting desired maskset peripheral file. Also uncomment the 
*		drivers which are used by your main application.  
*                                                                           
* AUTHOR: r9aabe       LOCATION: Austin,TX        LAST EDIT DATE: 05/12/03  
*                                                                                                                                                
******************************************************************************/

#ifndef PROJECTGLOBALS_H        /*prevent duplicated includes*/
#define PROJECTGLOBALS_H

/*****************************************************************************/
/*Global Includes															 */
/*****************************************************************************/

#include <hidef.h>				//Includes Code Warrior definitions	
#include "projectvectors.h"		//Includes Vector prototypes

/*****************************************************************************/
/* MCU_Maskset Selection:	     Uncomment one Target MCU_Maskset for        */
/*								 Development from the list of HCS12 Families */
/*****************************************************************************/

#define DP256_K79X

/******************************************************************************
* ROUTINE: MCU Peripherals
*
* DESCRIPTION:  includes MCU_Maskset peripheral file from project 
*				definitions library.        
*                                                                           
* NOTE: Modify by selecting which maskset to include into your main 
*		application by uncommenting the appropriate define at the top
*		of projectglobals.h (MCU_Maskset Selection)                                           
*                                                            
******************************************************************************/

#ifdef DP256_K79X
#include "per_DP256_K79X.h"	
#define Flash_Sector_Size 0x200	
#endif /*DP256_K79X*/

/*****************************************************************************/
/*Macro Definitions				(Defines below are functional examples)    	 */
/*****************************************************************************/

#define int_enable()  {asm andcc   #0xEF;}	  //interrupts enabled
#define int_disable() {asm orcc    #0x10;}	  //interrupts disabled
#define wait()        {asm wait;}			  //enter wait mode
#define stop_enable() {asm andcc   #0x7F;}	  //stop mode enabled
#define stop()        {asm stop;}			  //enter stop mode
#define nop()         {asm nop;}			  //enter NOP asm instruction
#define bgnd()        {asm bgnd; asm nop;}	  //enter BGND asm instruction

#define ON 1								  //ON 
#define OFF 0								  //OFF
#define TRUE 1								  //TRUE
#define FALSE 0								  //FALSE	
#define PASS 0u								  //PASS	
#define FAIL 1u								  //FAIL 	
#define SET 1u								  //SET	
#define CLEAR 0u							  //CLEAR	

/*****************************************************************************/
/*Software Driver Selection:      Uncomment necessary peripheral drivers     */
/*								  (Defines below are listed as examples)     */
/*****************************************************************************/

//#define ECT
//#define LCD
//#define PWM
//#define SCI

/******************************************************************************
* ROUTINE: Driver Includes
*
* DESCRIPTION:  includes from project driver library        
*                                                                           
* NOTE: Modify by selecting which drivers to include into your main 
*		application by uncommenting the appropriate define at the top
*		of projectglobals.h (Software Driver Selection) 
*		(Defines below are listed as examples)                                          
*                                                            
******************************************************************************/

#ifdef ECT
#include "ectdrv.h"
#endif /*ECT*/

#ifdef LCD
#include "lcddrv.h"
#endif /*LCD*/

#ifdef	PWM
#include "pwmdrv.h"
#endif /*PMW*/

#ifdef SCI
#include "scidrv.h"
#include "sci0_isr.h"
extern tU32 oscclk, pllclk, busclk; 
extern float sci_clk;	
#endif /*SCI*/


#endif /*PROJECTGLOBALS_H*/
