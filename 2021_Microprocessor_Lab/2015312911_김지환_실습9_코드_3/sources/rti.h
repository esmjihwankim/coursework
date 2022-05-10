#ifndef RTI_H        /*prevent duplicated includes*/
#define RTI_H

/*Includes*/
#include "projectglobals.h"
#include "helper.h"  

void init_rti(int s);
void rti_handler(void);
void rti_service(void);

#endif /*RTI_H*/
