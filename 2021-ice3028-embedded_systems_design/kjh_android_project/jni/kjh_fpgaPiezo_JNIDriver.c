#include <unistd.h>
#include <fcntl.h>
#include <assert.h>
#include <jni.h>

static int fd;

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaPiezo_1JNIDriver_openPiezo
  (JNIEnv * env, jobject obj){
	fd = open("/dev/kjh_fpgaPiezo", O_WRONLY);
	assert(fd != -1);
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaPiezo_1JNIDriver_writePiezo
  (JNIEnv * env, jobject obj, jchar data){
	write(fd, &data, 1);
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpgaPiezo_1JNIDriver_closePiezo
  (JNIEnv * env, jobject obj){
	close(fd);
}

