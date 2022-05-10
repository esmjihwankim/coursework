#ifndef LCD_H        /*prevent duplicated includes*/
#define LCD_H

/*Includes*/
#include "projectglobals.h"

#define CODE_CLR_DISP               0x01
#define CODE_RET_HOME               0x02
#define CODE_ENTRY_MODE_SET(ID, SH) ((0x04)|((ID)<<1)|(SH))
#define CODE_DISP_CTRL(D,C,B)       ((0x08)|((D)<<2)|((C)<<1)|(B))
#define CODE_CUR_DISP_SHIFT(SC, RL) ((0x10)|((SC)<<3)|((RL)<<2))
#define CODE_FUNC_SET(DL, N, F)     ((0x20)|((DL)<<4)|((N)<<3)|((F)<<2))
#define CODE_SET_CGRAM_ADDR(ADDR)   ((0x40)|((0x3F)&(ADDR)))
#define CODE_SET_DDRAM_ADDR(ADDR)   ((0x80)|((0x7F)&(ADDR)))

#define ENABLE_LCD()    (Regs.porta.bit.pta2 = 1)
#define DISABLE_LCD()   (Regs.porta.bit.pta2 = 0)

typedef unsigned char BYTE;
typedef unsigned int WORD;

void ms_delay(unsigned int ms);

void init_LCD(void);
void set_inst_register(BYTE code);
void write_data(BYTE data);
void write_string(BYTE offset, char *str);

#endif /* LCD_H */