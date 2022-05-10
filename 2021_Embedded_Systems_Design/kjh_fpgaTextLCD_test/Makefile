.SILENT:

include C:/AndroXStudio/Tools/make_comm

all: $(OBJECTS)
	$(CC) $(CFLAGS) $(EXEC_LDFLAGS) -save-temps -O2 -o kjh_fpgaTextLCD_test $(OBJECTS) \
		$(LLIB)/libgcc.a

	echo 
	echo "**** Install:" /data/local/tmp/kjh_fpgaTextLCD_test "****"
	$(ADB) push kjh_fpgaTextLCD_test /data/local/tmp
	$(ADB) shell chmod 755 /data/local/tmp/kjh_fpgaTextLCD_test
	echo 
	echo "**** Run ****"
	#$(ADB) shell /data/local/tmp/kjh_fpgaTextLCD_test

clean:
	rm -f *.o
	rm -f *.i
	rm -f *.s
	rm -f kjh_fpgaTextLCD_test
