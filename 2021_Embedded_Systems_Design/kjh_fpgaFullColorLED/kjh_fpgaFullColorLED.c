#include <linux/miscdevice.h>
#include <linux/platform_device.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <linux/mm.h>
#include <linux/list.h>
#include <asm/io.h>
#include <asm/uaccess.h>
#include <asm/cacheflush.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/errno.h>
#include <linux/types.h>
#include <linux/ioport.h>
#include <linux/delay.h>


#define DRIVER_AUTHOR			"Jihwan"
#define DRIVER_DESC			"full color led test program"

#define FULLCOLORLED_NAME    		"fpga_fullcolorled"
#define FULLCOLORLED_MODULE_VERSION	"FULL COLOR LED V0.1"
#define FULLCOLORLED_ADDRESS 		0x05000000
#define FULLCOLORLED_ADDRESS_RANGE 	0x1000

#define FULL_LED1	9
#define FULL_LED2	8
#define FULL_LED3	7
#define FULL_LED4	6
#define ALL_LED		5

static int fullled_usage = 0;
static int led_num=0;
static unsigned long  *fullled_ioremap;
static unsigned short *full_led_addr[4][3];


static int numOfLed = -1;

static int kjh_fpga_fullcolorled_open(struct inode * inode, struct file * file)
{
	if(fullled_usage != 0) return -EBUSY;

	fullled_ioremap=ioremap(FULLCOLORLED_ADDRESS,FULLCOLORLED_ADDRESS_RANGE);

	if(!check_mem_region((unsigned long)fullled_ioremap, FULLCOLORLED_ADDRESS_RANGE)) {
		request_mem_region((unsigned long)fullled_ioremap, FULLCOLORLED_ADDRESS_RANGE, FULLCOLORLED_NAME);
	}
	else	printk("driver: unable to register this!\n");


	full_led_addr[0][0] =(unsigned short *)((unsigned long)fullled_ioremap+0xa0);
	full_led_addr[0][1] =(unsigned short *)((unsigned long)fullled_ioremap+0xa2);
	full_led_addr[0][2] =(unsigned short *)((unsigned long)fullled_ioremap+0xa4);

	full_led_addr[1][0] =(unsigned short *)((unsigned long)fullled_ioremap+0xa6);
	full_led_addr[1][1] =(unsigned short *)((unsigned long)fullled_ioremap+0xa8);
	full_led_addr[1][2] =(unsigned short *)((unsigned long)fullled_ioremap+0xaa);

	full_led_addr[2][0] =(unsigned short *)((unsigned long)fullled_ioremap+0xb0);
	full_led_addr[2][1] =(unsigned short *)((unsigned long)fullled_ioremap+0xb2);
	full_led_addr[2][2] =(unsigned short *)((unsigned long)fullled_ioremap+0xb4);

	full_led_addr[3][0] =(unsigned short *)((unsigned long)fullled_ioremap+0xb6);
	full_led_addr[3][1] =(unsigned short *)((unsigned long)fullled_ioremap+0xb8);
	full_led_addr[3][2] =(unsigned short *)((unsigned long)fullled_ioremap+0xba);

	fullled_usage = 1;
	return 0;
}

static int kjh_fpga_fullcolorled_release(struct inode * inode, struct file * file)
{
	iounmap(fullled_ioremap);

	release_mem_region((unsigned long)fullled_ioremap, FULLCOLORLED_ADDRESS_RANGE);
	fullled_usage = 0;
	return 0;
}

static ssize_t kjh_fpga_fullcolorled_write(struct file * file, const char * buf, size_t length, loff_t * ofs)
{
	int ret,i=0,j=0;
	unsigned char data[3];

	printk("fpga_fullcolorled_write, \n");
	ret = copy_from_user(data,buf,length);
	for(j=0;j<3;j++)
	{
		if(data[j]%0x10 >= 0xA)
			data[j]+=0x06;
		if(data[j]%0x100 >= 0xA0)
			data[j]+=0x60;

		if(led_num != 4)
		{
			for(j=0;j<3;j++)
			{
				*full_led_addr[led_num][j] = data[j];
			}
		}
		else
		{
			for(i=0;i<4;i++)
			{
				for(j=0;j<3;j++)
				{
					*full_led_addr[i][j] = data[j];
				}
			}
		}
	}
	return length;
}

//static DEFINE_MUTEX(fpga_fullcolorled_mutex);
static long kjh_fpga_fullcolorled_ioctl(struct file * file, unsigned int cmd, unsigned long arg){
	switch(cmd)
	{
		case FULL_LED1:
			led_num = 0;
			break;
		case FULL_LED2:
			led_num = 1;
			break;
		case FULL_LED3:
			led_num = 2;
			break;
		case FULL_LED4:
			led_num = 3;
			break;
		case ALL_LED:
			led_num = 4;
			break;
	}

//	mutex_unlock(&fpga_fullcolorled_mutex);
	return 0;
}


static struct file_operations fpga_fullcolorled_fops = {
	.owner = THIS_MODULE,
	.open = kjh_fpga_fullcolorled_open,
	.release = kjh_fpga_fullcolorled_release,
//	.read = fpga_fullcolorled_read,
	.write = kjh_fpga_fullcolorled_write,
	.unlocked_ioctl = kjh_fpga_fullcolorled_ioctl,
};

static struct miscdevice fpga_fullcolorled_driver = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = "kjh_fpgaFullColorLed",
	.fops = &fpga_fullcolorled_fops,
};

static int kjh_fpga_fullcolorled_init(void){
	printk("kjh_fpga_fullcolorled_init, \n");
	
	return misc_register(&fpga_fullcolorled_driver);
}

static void kjh_fpga_fullcolorled_exit(void){
	printk("kjh_fpga_fullcolorled_exit, \n");

	misc_deregister(&fpga_fullcolorled_driver);
}

module_init(kjh_fpga_fullcolorled_init);
module_exit(kjh_fpga_fullcolorled_exit);

MODULE_AUTHOR("Jihwan");
MODULE_DESCRIPTION("fpga_fullcolorled driver test");
MODULE_LICENSE("Dual BSD/GPL");
