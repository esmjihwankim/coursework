
#include "main.h"
unsigned char *txbuffer_sci0; //text를 저장하는 버퍼이다. 
int txoffset_sci0;            //text문자열 길이를 알기위해 필요한 변수이다.
unsigned char *rxbuffer_sci0; //rx를 저장하는 버퍼이다.

/*********************************************************/
/*  시리얼 통신 0번 채널을 초기화 한다.				                       */
/*********************************************************/ 
void init_sci0(int baud_rate, unsigned char *rxbuf) 
{
/*sci를 초기화 하는 함수이다. bps와 문자열의 길이 그리고 송수신 interrupt를 사용할지 등을 결정한다.*/
  unsigned long oscclk, modclk;  //SCIBD register의 SBR을 설정하기 위한 변수
  unsigned short br;    //우리 얻고자 하는 bps를 저장하는 변수
  oscclk = 16000000;	  //MCU의 주파수는 16 MHz이다.
  modclk = (oscclk/2);	  //Set SCI module clock = (Oscillator Freq.)/2
  br = (  modclk/(16*baud_rate) );    //Set BR, SCI baud rate = (SCI module clock)/(16*BR)
/*위의 식들은 우리가 사용하는 MCU의 설정에 의해 정해지는 식이다. */

  Sci0.scibd.word =  ( 26 );  //설정한 BR 값을 SCIBD register에 저장
  Sci0.scicr1.byte = (0b00000000);  //SCI 설정 관련 register 초기화. Normal operation & 8 data bit format & Parity disabled
  Sci0.scicr2.byte = (0b00101100);  //SCI 설정 관련 register 초기화. transmit & receive & receive interrupt 활성화 
/* 여기서 transmit interrpt는 보낼 때 interrupt를 발생시키기 때문에 초기화 해 줄 필요없다. */ 
	txoffset_sci0 = 0;          
	rxbuffer_sci0 = rxbuf;
/*각각의 offset과 buffer를 초기화 한다.*/     
}
/*********************************************************/
/*  입력받은 문자열을 시리얼 통신으로 전송한다.                          */
/*  입력받은 문자열과 길이를 버퍼에 저장하고 송신 interrupt를 enable시켜     */
/*  MCU가 interrupt handler를 수행하도록 한다.                   */
/*********************************************************/ 
void write_sci0(unsigned char *text)
{
/*이 함수는 입력받은 문자열을 컴퓨터에 보내는 역할을 하는 함수이다. transmit interrupt를 발생시켜 sci interrupt handler함수를 호출하게 된다*/

	txbuffer_sci0 = text;
/*문자열 길이를 offset에 저장 시킨다.*/
	Sci0.scicr2.byte |= ( 0b10001000 );         //TIE & TE 활성화

}
/*****************************************************************/
//  시리얼 통신 송신 및 수신 인터럽트가 발생했을 때 처리되는 함수.                      
//  한 바이트의 문자가 송신 및 수신 될 때마다 인터럽트가 발생함                        
//  sci의 interrupt TDRE와 RDRF가 발생했을 때 호출되는 함수이다. 따라서 먼저 이 함수가 projectvectors.c에 등록이 되어 있어야 한다. 레지스터의 비트 패턴에 따라 송/수신 상태가 결정된다.        						 
/*****************************************************************/ 
void sci0_handler(void)
{
  Regs.portb.byte = ( 0b11111111 );   // 포트 B의 모든 핀을 1로 설정
  Pim.ptm.byte = ( 0b11000000 );      // 포트 M의 6,7번 핀을 1로 설정

  if(Sci0.scisr1.bit.rdrf == 1)   //수신 상태이면 RDRF는 반드시 1이 되어있다.
  {
        *rxbuffer_sci0 = Sci0.scidrl.byte;  // scidrl에 저장된 1bit 수신 데이터를 수신 버퍼에 저장    
        /*그렇게 수신한 데이터를 출력하기위해 rxbuffer의 첫 번째 자리부터 저장하게 된다. */
  	    /* Application code  */
  	    
        switch(*rxbuffer_sci0) {
            case '0':
                Regs.portb.byte = 0b11111111;
                break;
            case '1':
                Regs.portb.byte = 0b11111110;
                break;
            case '2':
                Regs.portb.byte = 0b11111100;
                break;
            case '3':
                Regs.portb.byte = 0b11111000;
                break;
            case '4':
                Regs.portb.byte = 0b11110000;
                break;
            case '5':
                Regs.portb.byte = 0b11100000;
                break;
            case '6':
                Regs.portb.byte = 0b11000000;
                break;
            case '7':
                Regs.portb.byte = 0b10000000;
                break;
            case '8':
                Regs.portb.byte = 0b00000000;
                break;
            default:
                break; 
        }
 	
  }
  else if (Sci0.scisr1.bit.tdre == 1)  
/*수신 상태가 아닌 송신 상태이면 TDRE가 1이되고 위와 같이 status와 비교해 주면 된다. */
  {
 
    Sci0.scidrl.byte = *txbuffer_sci0;    // scidrl에 송신할 데이터 저장
    txbuffer_sci0++;

    if(*txbuffer_sci0 == '\0')
    {
      Sci0.scicr2.byte &= 0b01111111;           // Transmitter Interrupt Enable Bit만 클리어
    }
  }
}