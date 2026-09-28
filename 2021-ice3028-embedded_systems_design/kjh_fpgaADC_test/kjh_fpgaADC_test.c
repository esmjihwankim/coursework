#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <asm/ioctl.h>      // For ADC_CH1_READ

#define ADC_IO 0x55
#define ADC_CH1_READ 	_IO(ADC_IO,0x31)
#define ADC_CH2_READ 	_IO(ADC_IO,0x32)
#define ADC_CH3_READ 	_IO(ADC_IO,0x32)
#define ADC_CH4_READ 	_IO(ADC_IO,0x32)


int main(void)
{
	int fd;
	if((fd = open("/dev/kjh_fpgaADC", O_RDWR | O_SYNC)) < 0){
		fprintf(stdout, "can't open the driver");
		exit(1);
	}

	int i;
	int value;
	value = ioctl(fd, ADC_CH1_READ, NULL, NULL);
	fprintf(stdout, "ADC Active ::");
	close(fd);
	return 0;
}
