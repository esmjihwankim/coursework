#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <ctype.h>

#define FULL_LED1 9
#define FULL_LED2 8
#define FULL_LED3 7
#define FULL_LED4 6

int fd;

void input_value(void)
{
        char value[3] = {0};

        printf("\ninput range 0 ~ 100 \n");
        printf("\ninput Red value : ");
        scanf("%d",&value[0]);
        printf("\ninput Green value : ");
        scanf("%d",&value[1]);
        printf("\ninput Blue value : ");
        scanf("%d",&value[2]);
        printf("\n");
        write(fd,value,3);
}

void print_menu(void)
{
        printf("\n");
        printf("==============================================\n");
        printf("                Select Menu\n");
        printf("----------------------------------------------\n");
        printf("   1.   Led1    -[1]\n");
        printf("   2.   Led2    -[2]\n");
        printf("   3.   Led3    -[3]\n");
        printf("   4.   Led4    -[4]\n");
        printf("   5.   Quit    -[5]\n");
        printf("----------------------------------------------\n");
        printf("==============================================\n");
}

int ItemSelect(void)
{
	char Menu;

	while(1) {
		print_menu();
		printf("\nSelected Item :  ");
		Menu = getchar();
		switch(Menu) {
			case '1':
				ioctl(fd,FULL_LED1); input_value(); break;
			case '2':
				ioctl(fd,FULL_LED2); input_value(); break;
			case '3':
				ioctl(fd,FULL_LED3); input_value(); break;
			case '4':
				ioctl(fd,FULL_LED4); input_value(); break;
			case '5':
				return 0;
		default: printf("\nNo Test Menu Selected"); break;
		}
	}
	return 0;
}

int main(void)
{
	if ((fd=open("/dev/fpga_fullcolorled",O_RDWR|O_SYNC)) < 0) {
		perror("/dev/fullcolorled open fail\n");
		exit(1);
	}

    	ItemSelect();

	close(fd);
 	return 0;
}
