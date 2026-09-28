#ifndef GPIO_H        /*prevent duplicated includes*/
#define GPIO_H

/*Includes*/
#include "projectglobals.h"

void init_portb(int direction);
void set_portb(int reverse, unsigned char data);  
unsigned char get_portb(void);

#endif /* GPIO_H */
