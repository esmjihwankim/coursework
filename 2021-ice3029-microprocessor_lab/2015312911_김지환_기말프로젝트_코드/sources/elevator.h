#ifndef ELEVATOR_H        /*prevent duplicated includes*/
#define ELEVATOR_H

#include "projectglobals.h"
#include "pwm.h"
#include "helper.h"
#include "atd.h" 



void operate(int floor);
void move(int time);



#endif /*ELEVATOR_H*/
