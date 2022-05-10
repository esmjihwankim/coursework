
#include <jni.h>
#include <fcntl.h>

int fd = 0;
JNIEXPORT jint JNICALL Java_edu_skku_jni_kjh_1fpga7segment_1JNIDriver_open7Driver
  (JNIEnv * env, jclass class, jstring path){
	jboolean iscopy;
	const char *path_utf = (*env)->GetStringUTFChars(env, path, &iscopy);
	fd = open(path_utf, O_WRONLY);
	(*env)->ReleaseStringUTFChars(env, path, path_utf);
	if (fd < 0)
		return -1;
	else
		return 1;
}

JNIEXPORT void JNICALL Java_edu_skku_jni_kjh_1fpga7segment_1JNIDriver_close7Driver
  (JNIEnv * env, jclass class){
	if (fd > 0)
		close(fd);
}

JNIEXPORT void Java_edu_skku_jni_kjh_1fpga7segment_1JNIDriver_write7Driver
  (JNIEnv * env, jclass class, jint value){
	if (fd>0) {
		write(fd, &value, 4);
	}
}


JNIEXPORT void Java_edu_skku_jni_kjh_1fpga7segment_1JNIDriver_ioctl7Driver
  (JNIEnv * env, jclass class, jint value){
	if (fd>0) {
		ioctl(fd, value, NULL, NULL);
	}
}
