package edu.skku.jni;

public class kjh_fpgaPiezo_JNIDriver {
	static {
		System.loadLibrary("kjh_piezo_lib");
	}
	
	public native void openPiezo();
	public native void writePiezo(char data);
	public native void closePiezo();
}

