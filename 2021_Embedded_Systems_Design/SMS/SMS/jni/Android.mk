LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := PiezoJNI
LOCAL_SRC_FILES := PiezoJNI.c

include $(BUILD_SHARED_LIBRARY)
