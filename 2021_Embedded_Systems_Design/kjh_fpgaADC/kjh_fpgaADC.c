#include <linux/input.h>
#include <linux/types.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/miscdevice.h>
#include <linux/slab.h>
#include <linux/fs.h>
#include <linux/ioport.h>
#include <asm/ioctl.h>
#include <asm/uaccess.h>

#define ADC_CONVERSION_REG	0x00
#define ADC_CONFIG_REG		0x02
#define ADC_TIMER_CYCLE_REG	0x03
#define ADC_TIME_32		0x01
#define ADC_CH1_LOW		0x04
#define ADC_CH1_HIGH		0x05
#define ADC_CH2_LOW		0x07
#define ADC_CH2_HIGH		0x08
#define ADC_CH3_LOW		0x0A
#define ADC_CH3_HIGH		0x0B
#define ADC_CH4_LOW		0x0D
#define ADC_CH4_HIGH		0x0E

#define ADC_SELECT_CH1		0x18
#define ADC_SELECT_CH2		0x28
#define ADC_SELECT_CH3		0x48
#define ADC_SELECT_CH4		0x88

#define ADC_IO		0x55
#define ADC_CH1_READ	_IO(ADC_IO, 0x31)
#define ADC_CH2_READ	_IO(ADC_IO, 0x32)
#define ADC_CH3_READ	_IO(ADC_IO, 0x33)
#define ADC_CH4_READ	_IO(ADC_IO, 0x34)

struct adc_data {
        struct i2c_client *client;
        struct device *dev;
        struct input_dev *idev;
};

static struct adc_data *adc_ptr;

static int m2_adc_i2c_read(struct i2c_client *client, char ch_select, char ch)
{
	int ret;
	int adc_result;
	u16 *data;
	ret = i2c_smbus_write_byte_data(client, ADC_CONFIG_REG, ch_select);
	if(ret < 0)
		printk(KERN_INFO "Debug --- i2c write err \n");
	ret = i2c_smbus_write_byte_data(client, ADC_TIMER_CYCLE_REG, ADC_TIME_32);
	if(ret < 0)
		printk(KERN_INFO "Debug --- i2c write err \n");
	ret = i2c_smbus_read_word_data(client,ADC_CONVERSION_REG);
	if(ret < 0)
		printk(KERN_INFO "Debug --- i2c read err \n");
	*data = swab16((u16)ret);
	adc_result = (*data&0x0fff)>>2;
	return adc_result;
}

static int m2_adc_open(struct inode *minode, struct file *mfile)
{
 	return 0;
}

static int m2_adc_release(struct inode *minode, struct file *mfile)
{

        return 0;
}

static int m2_adc_ioctl(struct file *file,unsigned int cmd, unsigned long arg)
{
	struct adc_data *adc;
	int adc_result;
	adc = adc_ptr;
	
	switch(cmd)
	{
	case ADC_CH1_READ:
		adc_result = m2_adc_i2c_read(adc->client,ADC_SELECT_CH1,ADC_CH1_HIGH);
		break;
	case ADC_CH2_READ:
		adc_result = m2_adc_i2c_read(adc->client,ADC_SELECT_CH2,ADC_CH2_HIGH);
		break;
	case ADC_CH3_READ:
		adc_result = m2_adc_i2c_read(adc->client,ADC_SELECT_CH3,ADC_CH3_HIGH);
		break;
	case ADC_CH4_READ:
		adc_result = m2_adc_i2c_read(adc->client,ADC_SELECT_CH4,ADC_CH4_HIGH);
		break;
	}
	return adc_result;
}

static struct file_operations m2_adc_fops = {
	.owner		= THIS_MODULE,
        .open		= m2_adc_open,
        .unlocked_ioctl	= m2_adc_ioctl,
        .release	= m2_adc_release,
};

static struct miscdevice m2_adc_driver = {
	.fops	= &m2_adc_fops,
	.name	= "kjh_fpgaADC",
	.minor 	= MISC_DYNAMIC_MINOR,
};

static int __devinit m2_adc_probe(struct i2c_client *client,
                                   const struct i2c_device_id *id)
{
    	struct adc_data *adc;
    	struct input_dev *idev;
	int error;

	adc = kzalloc(sizeof(struct adc_data), GFP_KERNEL);
	idev = input_allocate_device();
   	if (!adc || !idev) {
	    	dev_err(&client->dev, "failed to allocate driver data\n");
	    	error = -ENOMEM;
	    	goto err_free_mem;
	}
	
	if(!i2c_check_functionality(client->adapter, I2C_FUNC_I2C))
	{
		error = -ENODEV;
		goto err_free_mem;
	}

	adc->client = client;
	adc->dev = &client->dev;
	adc->idev = idev;

	i2c_set_clientdata(client,adc);

	adc_ptr = adc;
	
	error = misc_register(&m2_adc_driver);
	if (error) {
		dev_err(&client->dev, "failed to register input device\n");
		goto err_mpuirq_failed;
	}

	printk("m2_adc probe! \n");
	return 0;

err_mpuirq_failed:
	misc_deregister(&m2_adc_driver);

err_free_mem:
	input_free_device(idev);
	kfree(adc);
	return error;
}


static int __devexit m2_adc_remove(struct i2c_client *client)
{
	return misc_deregister(&m2_adc_driver);
}

static const struct i2c_device_id m2_adc_ids[] = {
       { "ad7993", 0x22 },
       { }
};
MODULE_DEVICE_TABLE(i2c, m2_adc_ids);

static struct i2c_driver m2_adc_i2c_driver = {
	.driver = {
        	.name  	= "kjh_fpgaADC",
		.owner  = THIS_MODULE,
	},
        .probe          = m2_adc_probe,
        .remove         = __devexit_p(m2_adc_remove),
        .id_table       = m2_adc_ids,
};

static int __init m2_adc_init(void)
{
        return misc_register(&m2_adc_driver);
}
module_init(m2_adc_init);

static void __exit m2_adc_exit(void)
{
		misc_deregister(&m2_adc_driver);
}
module_exit(m2_adc_exit);

MODULE_AUTHOR("Jihwan");
MODULE_DESCRIPTION("hanback adc driver");
MODULE_LICENSE("Dual BSD/GPL");

