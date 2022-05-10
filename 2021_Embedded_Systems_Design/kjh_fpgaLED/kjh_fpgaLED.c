#include <linux/kernel.h>
#include <linux/init.h>
#include <asm/uaccess.h>
#include <asm/io.h>
#include <linux/ioport.h>
#include <linux/fs.h>
#include <linux/miscdevice.h>
#include <linux/mutex.h>

#define LED_ADDRESS 0x05000020
#define LED_ADDRESS_RANGE 0x1000

#define DEVICE_NAME "kjh_fpgaled"

static int led_usage = 0;
static unsigned long *led_ioremap;

static int kjh_fpgaled_open(struct inode * inode, struct file * file){
	
	printk("kjh_fpgaled_open, \n");
	
	if (led_usage == -1)
		return -EBUSY;

	led_ioremap = ioremap(LED_ADDRESS, LED_ADDRESS_RANGE);

	if ( check_mem_region( (unsigned long) led_ioremap, LED_ADDRESS_RANGE)) {
		printk(KERN_WARNING "Can't get IO Region 0x%x\n", (unsigned int) led_ioremap);
		return -1;
}

	request_mem_region( (unsigned long) led_ioremap, LED_ADDRESS_RANGE, DEVICE_NAME);
	led_usage = 1;

	return 0;
}


static int kjh_fpgaled_release(struct inode * inode, struct file * file){

	printk("kjh_fpgaled_release, \n");

	release_mem_region( (unsigned long) led_ioremap, LED_ADDRESS_RANGE);
	iounmap(led_ioremap);

	led_usage = 0;
	return 0;
}


static ssize_t kjh_fpgaled_write(struct file * file, const char * buf, size_t length, loff_t * ofs){
	unsigned short *addr;
	unsigned char value;

	get_user(value, buf);
	printk("kjh_fpgaled_write, value : %d \n", value);
	addr = (unsigned short*)led_ioremap;
	*addr = value|0x100;

	return length;
}


static struct file_operations kjh_fpgaled_fops = {
	.owner = THIS_MODULE,
	.open = kjh_fpgaled_open,
	.release = kjh_fpgaled_release,
	//.read = kjh_fpgaled_read,
	.write = kjh_fpgaled_write,
	//.unlocked_ioctl = kjh_fpgaled_ioctl,
};

static struct miscdevice kjh_fpgaled_driver = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = "kjh_fpgaled",
	.fops = &kjh_fpgaled_fops,
};


static int kjh_fpgaled_init(void){
	printk("kjh_fpgaled_init, \n");

	return misc_register(&kjh_fpgaled_driver);
}

static void kjh_fpgaled_exit(void){
	printk("kjh_fpgaled_exit, \n");

	misc_deregister(&kjh_fpgaled_driver);
}

module_init(kjh_fpgaled_init);
module_exit(kjh_fpgaled_exit);

MODULE_AUTHOR("Jihwan Kim");
MODULE_DESCRIPTION("fpgaled driver");
MODULE_LICENSE("Dual BSD/GPL");


