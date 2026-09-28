#include <unistd.h>
#include <fcntl.h>
#include <assert.h>
#include <jni.h>

static int fd;

JNIEXPORT void JNICALL Java_edu_skku_sms_1jni_PiezoJNI_open
  (JNIEnv * env, jobject obj){
	fd = open("/dev/sms_fpgapiezo", O_WRONLY);
		assert(fd != -1);

}

JNIEXPORT void JNICALL Java_edu_skku_sms_1jni_PiezoJNI_write
  (JNIEnv * env, jobject obj, jchar data){
	write(fd, &data, 1);
}

JNIEXPORT void JNICALL Java_edu_skku_sms_1jni_PiezoJNI_close
  (JNIEnv * env, jobject obj){
	close(fd);
}
