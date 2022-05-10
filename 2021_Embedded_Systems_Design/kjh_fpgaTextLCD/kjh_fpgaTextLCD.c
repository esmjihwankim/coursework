#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <asm/uaccess.h>
#include <asm/io.h>
#include <linux/ioport.h>
#include <linux/fs.h>
#include <linux/miscdevice.h>
#include <linux/mutex.h>
#include <linux/delay.h>

#define TEXTLCD_ADDRESS			0x05000010
#define TEXTLCD_ADDRESS_RANGE 	0x1000

#define DEVICE_NAME			"kjh_fpgaTextLCD"

static int textlcd_usage = 0;
static unsigned long int *textlcd_ioremap;

// ------------------------------------

#define TEXTLCD_ON 		1
#define TEXTLCD_OFF 	2
#define TEXTLCD_INIT 	3
#define TEXT_CLEAR		4

#define TEXT_LINE1		5
#define TEXT_LINE2		6


static unsigned short int command;

void runCommand(void)
{
	command &= 0x00FF;
	*textlcd_ioremap = command | 0x0000;
	udelay(1000);
	*textlcd_ioremap = command | 0x0100;
	udelay(1000);
	*textlcd_ioremap = command | 0x0000;
	udelay(1000);
}

void writeCharacter(char ch)
{
	unsigned short int data;
	data = ch & 0x00FF;
	*textlcd_ioremap = 0x0400;
	udelay(1000);
	*textlcd_ioremap = data | 0x0500;
	udelay(1000);
	*textlcd_ioremap = data | 0x0400;
	udelay(1000);
}

void clearDisplay(void)
{
	command = 0x0001;
	runCommand();
}

void returnHome(void)
{
	command = 0x0002;
	runCommand();
}

void entryModeSet(int increase, int shift)
{
	command = 0x0004;
	command |= (increase << 1) + shift;			// == (increase << 1) | shift
	runCommand();
}

void displayOnOffControl(int display, int cursor, int blink)
{
	command = 0x0008;
	command |= (display << 2) + (cursor << 1) + blink;
	runCommand();
}

void cursorOrDisplayshift(int screenOrCursor, int rightOrLeft)
{
	command = 0x0010;
	command |= (screenOrCursor <<3) + (rightOrLeft << 2);
	runCommand();
}

void setFunctionSet(int dataLength, int row, int font)
{
	command = 0x0020;
	command |= (dataLength << 4) + (row << 3) + (font << 2);
	runCommand();
}

void setCGRamAddress(int address)
{
	command = 0x0040;
	command |= address;				// addr: [4-0]
	runCommand();
}

void setDDRamAddress(int address)
{
	command = 0x0080;
	command |= address;				// addr: [5-0]
	runCommand();
}

void readBusyFlagAndAddress(int *pBusyFlag, int *pAddressCounter)
{
	command = 0x0200;
	runCommand();

	*pBusyFlag = (command >> 7) & 0x01;
	*pAddressCounter = command & 0xEF;
}

void dataWriteToCGRamOrDDRam(int address)
{
	command = 0x0400;
	command |= address;			// addr: [7-0]
	runCommand();
}

void dataReadFromCGRamOrDDRam(int address)
{
	command = 0x0300;
	command |= address;			// addr: [7-0]

	runCommand();
}

void initializeTextLcd(void)
{
	setFunctionSet(1, 1, 0);				//1 - dataLen: 8, 1 - line: 2, 0 - font: 5 *7 dot
	displayOnOffControl(1, 0, 0);		//1 - display on, 0 - cursor off, 0 - cursor blink off
	clearDisplay();
	entryModeSet(1, 0);					// 1 - after data is read or written, curor pos increase, 0 - screen scroll off
	returnHome();
}

// ------------------------------------


static int fpga_textlcd_open(struct inode * inode, struct file * file)
{
	if (textlcd_usage == -1)
		return -EBUSY;

	textlcd_ioremap = ioremap(TEXTLCD_ADDRESS, TEXTLCD_ADDRESS_RANGE);

	if ( check_mem_region( (unsigned long int) textlcd_ioremap, TEXTLCD_ADDRESS_RANGE) /* != 0 */)
	{
		printk(KERN_WARNING "Can't get IO Region 0x%x\n", (unsigned int) textlcd_ioremap);
		return -1;
	}

	request_mem_region( (unsigned long int) textlcd_ioremap, TEXTLCD_ADDRESS_RANGE, DEVICE_NAME);
	textlcd_usage = 1;

	return 0;
}

static int fpga_textlcd_release(struct inode * inode, struct file * file)
{
	release_mem_region( (unsigned long int) textlcd_ioremap, TEXTLCD_ADDRESS_RANGE);
	iounmap(textlcd_ioremap);

	textlcd_usage = 0;
	return 0;
}

/* not use
static ssize_t fpga_textlcd_read(struct file * file, char * buf, size_t length, loff_t * ofs)
{
	printk("fpga_textlcd_read, \n");

	return 0;
}
*/

static ssize_t fpga_textlcd_write(struct file * file, const char * buf, size_t length, loff_t * ofs)
{
	int i;
	int size;
	unsigned char str[20];

	size = (length < 20) ? length : 20;

	copy_from_user(str, buf, length);
	for (i = 0; i < size ; ++i)
		writeCharacter(str[i]);

	return length;
}

static DEFINE_MUTEX(fpga_textlcd_mutex);
static long fpga_textlcd_ioctl(struct file * file, unsigned int cmd, unsigned long arg)
{

	switch(cmd){
	case TEXTLCD_ON:
		displayOnOffControl(1, 0, 0);
		break;
	case TEXTLCD_OFF:
		displayOnOffControl(0, 0, 0);
		break;
	case TEXTLCD_INIT:
		initializeTextLcd();
		break;
	case TEXT_CLEAR:
		clearDisplay();
		break;
	case TEXT_LINE1:
		setDDRamAddress(0x00);
		break;
	case TEXT_LINE2:
		setDDRamAddress(0x40);
		break;

	default:
		mutex_unlock(&fpga_textlcd_mutex);
		return ENOTTY;
	}

	mutex_unlock(&fpga_textlcd_mutex);
	return 0;
}


static struct file_operations fpga_textlcd_fops = {
	.owner = THIS_MODULE,
	.open = fpga_textlcd_open,
	.release = fpga_textlcd_release,
//	.read = fpga_textlcd_read,
	.write = fpga_textlcd_write,
	.unlocked_ioctl = fpga_textlcd_ioctl,
};

static struct miscdevice fpga_textlcd_driver = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = "kjh_fpgaTextLCD",
	.fops = &fpga_textlcd_fops,
};

static int fpga_textlcd_init(void){
	printk("fpga_textlcd_init, \n");

	return misc_register(&fpga_textlcd_driver);
}

static void fpga_textlcd_exit(void){
	printk("fpga_textlcd_exit, \n");

	misc_deregister(&fpga_textlcd_driver);

}

module_init(fpga_textlcd_init);
module_exit(fpga_textlcd_exit);

MODULE_AUTHOR("Jihwan");
MODULE_DESCRIPTION("fpga_textlcd driver test");
MODULE_LICENSE("Dual BSD/GPL");
