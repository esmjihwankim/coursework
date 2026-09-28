#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/errno.h>
#include <linux/types.h>
#include <asm/fcntl.h>
#include <linux/ioport.h>
#include <linux/delay.h>
#include <linux/miscdevice.h>
#include <linux/platform_device.h>
#include <linux/file.h>
#include <asm/ioctl.h>
#include <asm/uaccess.h>
#include <asm/io.h>

#define DRIVER_AUTHOR "Jihwan"
#define DRIVER_DESC "7-Segment program"
#define DEVICE_NAME "kjh_fpga7segment"

#define SEGMENT_ADDRESS_GRID 0x05000030
#define SEGMENT_ADDRESS_DATA 0x05000032
#define SEGMENT_ADDRESS_RANGE 0x1000
#define MODE_0_TIMER_FORM 0x0
#define MODE_1_CLOCK_FORM 0x1

static unsigned int segment_usage = 0;
static unsigned long *segment_data;
static unsigned long *segment_grid;
static int mode_select = 0x0;

static int kjh_fpga7segment_open(struct inode * inode, struct file * file){
	printk("kjh_fpga7segment_open, \n");
	if(segment_usage != 0) return -EBUSY;

	segment_grid =  ioremap(SEGMENT_ADDRESS_GRID, 					SEGMENT_ADDRESS_RANGE);
	segment_data =  ioremap(SEGMENT_ADDRESS_DATA, 					SEGMENT_ADDRESS_RANGE);

	if(!check_mem_region((unsigned long) segment_data, 				SEGMENT_ADDRESS_RANGE)
		&& !check_mem_region((unsigned long)segment_grid, 			SEGMENT_ADDRESS_RANGE))
	{
		request_region((unsigned long)segment_grid, 					SEGMENT_ADDRESS_RANGE, DEVICE_NAME);
		request_region((unsigned long)segment_data, 					SEGMENT_ADDRESS_RANGE, DEVICE_NAME);
	}
	else printk("driver : unable to register this!\n");

	segment_usage = 1;
	return 0;
}

static int kjh_fpga7segment_release(struct inode * inode, struct file * file){
	printk("kjh_fpga7segment_release, \n");
	iounmap(segment_grid);
	iounmap(segment_data);

	release_region((unsigned long)segment_data, 					SEGMENT_ADDRESS_RANGE);
	release_region((unsigned long)segment_grid, 					SEGMENT_ADDRESS_RANGE);

	segment_usage = 0;
	return 0;
}


unsigned short Getsegmentcode (short x)
{
	unsigned short code;
	switch (x) {
		case 0x0 : code = 0xfc; break;
		case 0x1 : code = 0x60; break;
		case 0x2 : code = 0xda; break;
		case 0x3 : code = 0xf2; break;
		case 0x4 : code = 0x66; break;
		case 0x5 : code = 0xb6; break;
		case 0x6 : code = 0xbe; break;
		case 0x7 : code = 0xe4; break;
		case 0x8 : code = 0xfe; break;
		case 0x9 : code = 0xf6; break;
		case 0xa : code = 0xfa; break;
		case 0xb : code = 0x3e; break;
		case 0xc : code = 0x1a; break;
		case 0xd : code = 0x7a; break;
		case 0xe : code = 0x9e; break;
		case 0xf : code = 0x8e; break;
		default : code = 0; break;
	}
	return code;
}

static ssize_t kjh_fpga7segment_write(struct file * file, const char * buf, size_t length, loff_t * ofs){
	unsigned char data[6];
	unsigned char digit[6]={0x20, 0x10, 0x08, 0x04, 0x02, 0x01};
	unsigned int i,num,ret;
	unsigned int count=0,temp1,temp2;

	ret=copy_from_user(&num,buf,4);
	printk("kjh_fpga7segment_write: %d \n", num);

	count = num;

	if(num!=0) {
		data[5]=Getsegmentcode(count/100000);
		temp1=count%100000;
		data[4]=Getsegmentcode(temp1/10000);
		temp2=temp1%10000;
		data[3]=Getsegmentcode(temp2/1000);
		temp1=temp2%1000;
		data[2]=Getsegmentcode(temp1/100);
		temp2=temp1%100;
		data[1]=Getsegmentcode(temp2/10);
		data[0]=Getsegmentcode(temp2%10);


		switch (mode_select) {
    			case MODE_0_TIMER_FORM:
    				break;
    			case MODE_1_CLOCK_FORM:
    				data[4] += 1;
    				data[2] += 1;
    				break;
		}

		for(i=0;i<6;i++) {
    			*segment_grid = digit[i];
    			*segment_data = data[i];
    			mdelay(1);
		}
	}

	*segment_grid = ~digit[0];
	*segment_data = 0;

	return length;
}

	
static long kjh_fpga7segment_ioctl(struct file * file, unsigned int cmd, unsigned long arg){
	printk("kjh_fpga7segment_ioctl, %d \n", cmd);

	switch(cmd) {
		case MODE_0_TIMER_FORM:
   		 	mode_select=0x00;
    			break;
		case MODE_1_CLOCK_FORM:
    			mode_select=0x01;
    			break;
		default:
   			return -EINVAL;
    	}
	return 0;
}

static struct file_operations kjh_fpga7segment_fops = {
	.owner = THIS_MODULE,
	.open = kjh_fpga7segment_open,
	.release = kjh_fpga7segment_release,
	//.read = kjh_fpga7segment_read,
	.write = kjh_fpga7segment_write,
	.unlocked_ioctl = kjh_fpga7segment_ioctl,
};

static struct miscdevice kjh_fpga7segment_driver = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = "kjh_fpga7segment",
	.fops = &kjh_fpga7segment_fops,
};


static int kjh_fpga7segment_init(void){
	printk("kjh_fpga7segment_init, \n");

	return misc_register(&kjh_fpga7segment_driver);
}

static void kjh_fpga7segment_exit(void){
	printk("kjh_fpga7segment_exit, \n");

	misc_deregister(&kjh_fpga7segment_driver);

}

module_init(kjh_fpga7segment_init);
module_exit(kjh_fpga7segment_exit);

MODULE_AUTHOR(DRIVER_AUTHOR);
MODULE_DESCRIPTION(DRIVER_DESC);
MODULE_LICENSE("Dual BSD/GPL");
