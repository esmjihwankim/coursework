LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := kjh_led_lib
LOCAL_SRC_FILES := kjh_fpgaLED_JNIDriver.c 
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)

include $(CLEAR_VARS)

LOCAL_MODULE    := kjh_7segment_lib
LOCAL_SRC_FILES := kjh_fpga7segment_JNIDriver.c 
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)

include $(CLEAR_VARS)

LOCAL_MODULE    := kjh_textlcd_lib
LOCAL_SRC_FILES := kjh_fpgaTextLCD_JNIDriver.c 
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)


include $(CLEAR_VARS)

LOCAL_MODULE    := kjh_piezo_lib
LOCAL_SRC_FILES := kjh_fpgaPiezo_JNIDriver.c 
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)


include $(CLEAR_VARS)

LOCAL_MODULE    := kjh_dotmatrix_lib
LOCAL_SRC_FILES := kjh_fpgaDotMatrix_JNIDriver.c 
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)