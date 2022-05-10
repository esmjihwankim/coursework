#ifndef HELPER_H
#define HELPER_H

#include "projectglobals.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pwm.h"
#include "lcd.h"
#include "7segment.h"
#include "sci.h"
#include "rti.h"


unsigned char convertADCLevel(int cnt);

// LCD 
void showADCLevelOnLCD(void);
void showBufferingOnLCD(int* position);

// Segment
void spin7SegmentClockwise(void);
void spin7SegmentAntiClockwise(void);
void openCloseDoor(void);


void parse(char* buffer);
void showError(int error_type);


#endif /* HELPER_H */