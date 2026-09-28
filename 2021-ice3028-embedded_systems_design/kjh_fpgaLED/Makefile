.SILENT:

include C:/AndroXStudio/Tools/make_adb

export ARCH=arm
export CROSS_COMPILE=arm-linux-androideabi-

ifneq ($(KERNELRELEASE),)
obj-m := kjh_fpgaLED.o
else
KDIR := /platform/linux
all:
	$(MAKE) -C $(KDIR) M=$(shell pwd) modules

	echo 
	echo "**** Install:" /system/lib/modules/kjh_fpgaLED.ko "****"
	$(ADB) push kjh_fpgaLED.ko /system/lib/modules/
	$(ADB) shell chmod 644 /system/lib/modules/kjh_fpgaLED.ko
	echo 
	echo "**** Load Module:" /system/lib/modules/kjh_fpgaLED.ko "****"
	$(ADB) shell toolbox rmmod kjh_fpgaLED > /dev/null
	$(ADB) shell insmod /system/lib/modules/kjh_fpgaLED.ko
	$(ADB) shell lsmod | grep kjh_fpgaLED
	echo

endif

clean:
	rm -f *.symvers
	rm -f *.ko
	rm -f *.o
	rm -f *.mod.c
	rm -f *.order
	rm -f .*.cmd
	rm -rf .tmp_versions
