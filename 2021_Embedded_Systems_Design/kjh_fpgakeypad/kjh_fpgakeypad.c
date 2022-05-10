#include <linux/init.h>
#include <linux/module.h>
//#include <mach/hardware.h>
#include <asm/uaccess.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/types.h>
#include <asm/ioctl.h>
#include <linux/ioport.h>
#include <asm/io.h>
#include <linux/delay.h>
#include <linux/timer.h>
#include <linux/signal.h>
#include <linux/sched.h>
#include <linux/input.h>
#define DRIVER_AUTHOR		"Hanback Electronics"
#define DRIVER_DESC		"KEYPAD program"

#define KEYPAD_NAME 		"kjh_fpgakeypad"
#define KEYPAD_MODULE_VERSION 	"DOTMATRIX V1.0"
#define KEYPAD_PHY_ADDR		0x05000000
#define KEYPAD_ADDR_RANGE 		0x1000
#define TIMER_INTERVAL 35

static struct timer_list mytimer;
//static int keypad_usage = 0;
static unsigned short value;
static unsigned long  keypad_ioremap;
static unsigned short *keypad_row_addr,*keypad_col_addr, *keypad_check_addr;

char keypad_fpga_keycode[16] = {
		2,3,4,5,
		6,7,8,9,
		10,11,16,17,
		18,19,20,21
};

static struct input_dev *idev;
void mypollingfunction(unsigned long data);

static int kjh_fpgakeypad_open(struct inode * inode, struct file * file)
{
	keypad_col_addr =(unsigned short *)(keypad_ioremap+0x70);
	keypad_row_addr =(unsigned short *)(keypad_ioremap+0x72);
	
	init_timer(&mytimer);

	mytimer.expires = get_jiffies_64() + TIMER_INTERVAL;
	mytimer.function = &mypollingfunction;

	add_timer(&mytimer);

	return 0;
}

static int kjh_fpgakeypad_release(struct inode * inode, struct file * file)
{
	del_timer(&mytimer);

	return 0;
}

static int kjh_fpgakeypad_init(void){
	int result;
	int i=0;

	keypad_ioremap = (unsigned long)ioremap(KEYPAD_PHY_ADDR, KEYPAD_ADDR_RANGE);

	if(!check_mem_region(keypad_ioremap, KEYPAD_ADDR_RANGE)) {
		request_mem_region(keypad_ioremap, KEYPAD_ADDR_RANGE, KEYPAD_NAME);
	} else {
		printk("FPGA KEYPAD Memory Alloc Failed!\n");
		return -1;
	}
	
	keypad_check_addr = (unsigned short*)(keypad_ioremap+0x92);
	if(*keypad_check_addr != 0x2a) {
		printk("HBE-SM5-S4210 M3 Board is not exist...,0x%x\r\n", *keypad_check_addr);
		iounmap((unsigned long*)keypad_ioremap);
		release_region(keypad_ioremap, KEYPAD_ADDR_RANGE);
		return -1;
	}

	idev = input_allocate_device();

	set_bit(EV_KEY, idev->evbit);
	set_bit(EV_KEY, idev->keybit);

	for(i=0; i<30; i++)
		set_bit(i & KEY_MAX, idev->keybit);

	idev->name = "fpga-keypad";
	idev->id.vendor = 0x1002;
	idev->id.product = 0x1002;
	idev->id.bustype = BUS_HOST;
	idev->phys = "keypad/input1";
	idev->open = kjh_fpgakeypad_open;
	idev->close = kjh_fpgakeypad_release;

	result = input_register_device(idev);

	if(result < 0) {
		printk("FPGA KEYPAD Register Faild... \n");
		return result;
	}

	return 0;
}

static void kjh_fpgakeypad_exit(void){
	printk("kjh_fpgakeypad_exit, \n");
	iounmap((unsigned long*)keypad_ioremap);

	release_mem_region(keypad_ioremap, KEYPAD_ADDR_RANGE);

	input_unregister_device(idev);
}

void mypollingfunction(unsigned long data)
{
	int j=1,k,i;
	int funtion_key = 0;

	unsigned char tmp[4] = {0x01, 0x02, 0x04, 0x08};

	value =0;
	for(i=0;i<4;i++) {
		*keypad_row_addr = tmp[i];
		value = *keypad_col_addr & 0x0f;
		if(value > 0) {
			for(k=0;k<4;k++) {
				if(value == tmp[k]) {
					value = j+(i*4);
					funtion_key = keypad_fpga_keycode[value-1];
					if(value != 0x00) goto stop_poll;
				}
				j++;
			}
		}
	}
	stop_poll:
	if(value > 0) {
		if(*keypad_check_addr == 0x2a) {
			input_report_key(idev, funtion_key ,1);
			input_report_key(idev, funtion_key ,0);
			input_sync(idev);
			// kill_pid(id,SIGUSR1,1);
		}
	}
	else
		*keypad_row_addr = 0x00;

	mytimer.expires = get_jiffies_64() + TIMER_INTERVAL;
	add_timer(&mytimer);
}

module_init(kjh_fpgakeypad_init);
module_exit(kjh_fpgakeypad_exit);

MODULE_AUTHOR("Hanback");
MODULE_DESCRIPTION("kjh_fpgakeypad driver test");
MODULE_LICENSE("Dual BSD/GPL");
