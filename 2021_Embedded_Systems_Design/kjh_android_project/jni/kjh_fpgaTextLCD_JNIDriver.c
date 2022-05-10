#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <assert.h>
#include <jni.h>
#define TEXTLCD_ON 		1
#define TEXTLCD_OFF 	2
#define TEXTLCD_INIT 	3
#define TEXTLCD_CLEAR	4

#define TEXTLCD_LINE1		5
#define TEXTLCD_LINE2		6

static int fd;

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaTextLCD_1JNIDriver_on
  (JNIEnv * env, jobject obj){
	if (fd == 0)
		fd = open("/dev/kjh_fpgaTextLCD", O_WRONLY);
	assert(fd != 0);

	ioctl(fd, TEXTLCD_ON);
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaTextLCD_1JNIDriver_off
  (JNIEnv * env, jobject obj){
	if (fd )
	{
		ioctl(fd, TEXTLCD_OFF);
		close(fd);
	}

	fd = 0;
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaTextLCD_1JNIDriver_initialize
  (JNIEnv * env, jobject obj){
	if (fd == 0)
		fd = open("/dev/kjh_fpgaTextLCD", O_WRONLY);
	assert(fd != -1);

	ioctl(fd, TEXTLCD_INIT);
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaTextLCD_1JNIDriver_clear
  (JNIEnv * env, jobject obj){
	//if (fd )
		ioctl(fd, TEXTLCD_CLEAR);
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaTextLCD_1JNIDriver_print1Line
  (JNIEnv * env, jobject obj, jstring msg){
	const char *str;

	if (fd )
	{
		str = (*env)->GetStringUTFChars(env, msg, 0);
		ioctl(fd, TEXTLCD_LINE1);
		write(fd, str, strlen(str));
		(*env)->ReleaseStringUTFChars(env, msg, str);
	}

}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaTextLCD_1JNIDriver_print2Line
  (JNIEnv * env, jobject obj, jstring msg){
	const char *str;

	if (fd )
	{
		str = (*env)->GetStringUTFChars(env, msg, 0);
		ioctl(fd, TEXTLCD_LINE2);
		write(fd, str, strlen(str));
		(*env)->ReleaseStringUTFChars(env, msg, str);
	}
}
