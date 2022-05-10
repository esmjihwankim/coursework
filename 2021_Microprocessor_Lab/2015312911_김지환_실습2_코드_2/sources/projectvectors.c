/******************************************************************************
*                                             COPYRIGHT (c) MOTOROLA 2003   
* FILE NAME: projectvectors.c                                             
*                                                                           
* PURPOSE: source file which includes all DP256 (K79X) interrupt handlers
*		     							 
*                                                                           
* DESCRIPTION:  project vectors (interrupt handlers)        
*                                                                           
* NOTE: Interrupt vectors must point to fixed paged address. From the fixed
* 		routine a call can redirect to paged memory. 
*                                                                           
* AUTHOR: r9aabe    LOCATION: Austin,TX     LAST EDIT DATE: 05/12/03
*                                                                                             
******************************************************************************/

/*Include files */

#include "projectvectors.h"

/*Warning Disable*/

#pragma MESSAGE DISABLE C12004		//Warning: Far Keyword ignored for Function

/*Local Prototypes*/

void software_trap(void);

//************************************************************************
// SOFTWARE TRAP FUNCTION
// DESCRIPTION:
// Function that traps  all unexpected interrupts.  Used for debugging 
// software to find runaway code.
//
        
void software_trap(void){ for(;;); }

//************************************************************************
// UNUSED ISR
// DESCRIPTION:
// Takes place of undefined vectors. 
// Used for reserved vector spaces
//
#pragma CODE_SEG NON_BANKED        
interrupt void unused_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// PWM SHUTDOWN ISR
// DESCRIPTION:
// Interrupt asserted at the beginning of emergency shutdown initiated 
// on PWM7. PWM pin state will default and interrupt taken.
//
#pragma CODE_SEG NON_BANKED        
interrupt void pwm_shutdown_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// PORTP ISR
// DESCRIPTION:
// Interrupt asserted on a PORTP per pin basis, rising or falling edge. 
// Triggered by input transistion and stored as a flag.
//
#pragma CODE_SEG NON_BANKED 
interrupt void portp_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN4 TRANSMIT ISR
// DESCRIPTION:
// Interrupt asserted when at least one of three transmit buffers empty. 
// 
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan4_tx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN4 RECEIVE ISR
// DESCRIPTION:
// Interrupt asserted when a message has been received and shifted into 
// the forground buffer of the receiver FIFO.
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan4_rx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN4 ERROR ISR
// DESCRIPTION:
// Interrupt asserted when overrun, error or warning on the receive buffer. 
// 
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan4_error_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN4 WAKEUP ISR
// DESCRIPTION:
// Interrupt asserted with CAN activity during MSCAN internal sleep. 
// 
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan4_wakeup_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN3 TRANSMIT ISR
// DESCRIPTION:
// Interrupt asserted when at least one of three transmit buffers empty. 
// 
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan3_tx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN3 RECEIVE ISR
// DESCRIPTION:
// Interrupt asserted when a message has been received and shifted into 
// the forground buffer of the receiver FIFO.
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan3_rx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN3 ERROR ISR
// DESCRIPTION:
// Interrupt asserted when overrun, error or warning on the receive buffer.
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan3_error_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN3 WAKEUP ISR
// DESCRIPTION:
// Interrupt asserted with CAN activity during MSCAN internal sleep.
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan3_wakeup_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN2 TRANSMIT ISR
// DESCRIPTION:
// Interrupt asserted when at least one of three transmit buffers empty.
//
#pragma CODE_SEG NON_BANKED 
interrupt void mscan2_tx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN2 RECEIVE ISR
// DESCRIPTION:
// Interrupt asserted when a message has been received and shifted into 
// the forground buffer of the receiver FIFO.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan2_rx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN2 ERROR ISR
// DESCRIPTION:
// Interrupt asserted when overrun, error or warning on the receive buffer.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan2_error_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN2 WAKEUP ISR
// DESCRIPTION:
// Interrupt asserted with CAN activity during MSCAN internal sleep.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan2_wakeup_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN1 TRANSMIT ISR
// DESCRIPTION:
// Interrupt asserted when at least one of three transmit buffers empty.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan1_tx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN1 RECEIVE ISR
// DESCRIPTION:
// Interrupt asserted when a message has been received and shifted into 
// the forground buffer of the receiver FIFO.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan1_rx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN1 ERROR ISR
// DESCRIPTION:
// Interrupt asserted when overrun, error or warning on the receive buffer.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan1_error_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN1 WAKEUP ISR
// DESCRIPTION:
// Interrupt asserted with CAN activity during MSCAN internal sleep.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan1_wakeup_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN0 TRANSMIT ISR
// DESCRIPTION:
// Interrupt asserted when at least one of three transmit buffers empty.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan0_tx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN0 RECEIVE ISR
// DESCRIPTION:
// Interrupt asserted when a message has been received and shifted into 
// the forground buffer of the receiver FIFO.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan0_rx_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN0 ERROR ISR
// DESCRIPTION:
// Interrupt asserted when overrun, error or warning on the receive buffer.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan0_error_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// MSCAN0 WAKEUP ISR
// DESCRIPTION:
// Interrupt asserted with CAN activity during MSCAN internal sleep.
//
#pragma CODE_SEG NON_BANKED
interrupt void mscan0_wakeup_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// FLASH ISR
// DESCRIPTION:
// Interrupt asserted upon command completion or the address, data or  
// command buffers are empty.
//
#pragma CODE_SEG NON_BANKED
interrupt void flash_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// EEPROM ISR
// DESCRIPTION:
// Interrupt asserted upon command completion or the command buffers 
// are empty.
//
#pragma CODE_SEG NON_BANKED
interrupt void eeprom_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SPI2 ISR
// DESCRIPTION:
// Interrupt asserted when SPIF or MODF flags set. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void spi2_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SPI1 ISR
// DESCRIPTION:
// Interrupt asserted when SPIF or MODF flags set.
//
#pragma CODE_SEG NON_BANKED
interrupt void spi1_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// IIC ISR
// DESCRIPTION:
// Interrupt asserted when arbitration lost, byte transfer, or address detect. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void iic_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// BDLC ISR
// DESCRIPTION:
// Interrupt asserted by general BDLC interrupt including wakeup. Source
// resolved by register(s) flags.
//
#pragma CODE_SEG NON_BANKED
interrupt void bdlc_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// CRG SELF CLOCK MODE ISR
// DESCRIPTION:
// Interrupt asserted when self clock mode engaged. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void crg_scm_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// CRG PLL LOCK CONDITION CHANGED ISR
// DESCRIPTION:
// Interrupt asserted when lock condition of the PLL has changed.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void crg_pll_lock_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT PULSE ACCUMATATOR B OVERFLOW ISR
// DESCRIPTION:
// Interrupt asserted when pulse accumulator B overflows. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void pa_b_overflow_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT MODULUS DOWN COUNTER UNDERFLOW ISR
// DESCRIPTION:
// Interrupt asserted when modulus down counter underflows. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_mdc_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// PORTH ISR
// DESCRIPTION:
// Interrupt asserted on PORTH pin edge, saved as a flag. 
// All port pins serviced by one vector.
//
#pragma CODE_SEG NON_BANKED
interrupt void porth_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// PORTJ ISR
// DESCRIPTION:
// Interrupt asserted on PORTJ pin edge, saved as a flag. 
// All port pins serviced by one vector.
//
#pragma CODE_SEG NON_BANKED
interrupt void portj_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ATD1 SEQUENCE COMPLETE ISR
// DESCRIPTION:
// Interrupt asserted upon completion of ATD1 sequence. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void atd1_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ATD0 SEQUENCE COMPLETE ISR
// DESCRIPTION:
// Interrupt asserted upon completion of ATD0 sequence. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void atd0_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SCI1 ISR
// DESCRIPTION:
// Interrupt asserted from one of five sources. Two transmit and one receive.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void sci1_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SCI0 ISR
// DESCRIPTION:
// Interrupt asserted from one of five sources. Two transmit and one receive. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void sci0_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SPI0 ISR
// DESCRIPTION:
// Interrupt asserted from one of three sources. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void spi0_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// PULSE ACCUMULATOR A EDGE ISR
// DESCRIPTION:
// Interrupt asserted when edge received on Pulse Accumulator A. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void pa_a_edge_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// PULSE ACCUMULATOR A OVERFLOW ISR
// DESCRIPTION:
// Interrupt asserted upon Pulse Accumulator A overflow. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void pa_a_overflow_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT OVERFLOW ISR
// DESCRIPTION:
// Interrupt asserted upon ECT main timer overflow. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_overflow_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH7 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 7 event. 
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch7_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH6 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 6 event.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch6_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH5 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 5 event.
//
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch5_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH4 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 4 event.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch4_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH3 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 3 event.
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch3_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH2 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 2 event.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch2_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH1 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 1 event.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch1_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// ECT CH0 ISR
// DESCRIPTION:
// Interrupt asserted upon channel 0 event.
//
//
#pragma CODE_SEG NON_BANKED
interrupt void ect_ch0_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// REAL TIME ISR
// DESCRIPTION:
// Interrupt asserted when REAL-TIME interrupt period elapses. Operates 
// from OSCCLK.
// 
//
#pragma CODE_SEG NON_BANKED
interrupt void rti_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// INTERRUPT REQUEST PIN ISR
// DESCRIPTION:
// Interrupt asserted at IRQ PIN event. The event can be edge or level
// triggered. For edge, the interrupt is lateched internally. Internal 
// latch cleared when ISR taken.
// 
#pragma CODE_SEG NON_BANKED
interrupt void irq_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// EXTERNAL INTERRUPT REQUEST PIN ISR
// DESCRIPTION:
// Interrupt asserted on XIRQ low level event. ISR routine should handshake 
// with interrupt source to release the pin. XIRQ is enabled by clearing the
// X-bit. After enabled, disabled only after POR. 
//
#pragma CODE_SEG NON_BANKED
interrupt void xirq_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SOFTWARE INTERRUPT INSTRUCTION ISR
// DESCRIPTION:
// Interrupt asserted when SWI instruction executed. This acts as a hook 
// into on-board monitors and development instructions.
//
#pragma CODE_SEG NON_BANKED
interrupt void swi_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// UNIMPLIMENTED INSTRUCTION (OPCODE) TRAP ISR
// DESCRIPTION:
// Interrupt asserted when unimplimented opcode encountered. The stacked 
// address can be used to determine te source of the opcode.
//
#pragma CODE_SEG NON_BANKED
interrupt void trap_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// COMPUTER OPERATING PROPERLY (WATCHDOG) TIMER ISR
// DESCRIPTION:
// Interrupt asserted upon COP timeout. Operates from OSCCLK.
// To kick the dog write 55h then AAh to ARMCOP. Window COP bit extends
// basic operation by having a valid write during a percentage of the COP 
// window.
//
#pragma CODE_SEG NON_BANKED
interrupt void cop_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT

//************************************************************************
// SELF CLOCK-MODE ISR
// DESCRIPTION:
// Interrupt asserted when either entry or exit from Self-Clock Mode (SCM). 
// Clock Quality Checker is used to determine entery into SCM. The Clock
// Quality Checker provides a better clock check beyond the Clock Moitor. 
// A period of 50,000 PLL clocks is called a check-window. 4096 OSC clock 
// edges within a check-window means OSC OK. After 50 window tries IC will 
// enter PLL Self Clock (1Mz to 5MHz).
//
#pragma CODE_SEG NON_BANKED
interrupt void clockmonitor_isr(void){ (void) software_trap(); }
#pragma CODE_SEG DEFAULT      


/*Warning Enable*/

#pragma MESSAGE WARNING C12004		//Warning: Far Keyword ignored for Function       

