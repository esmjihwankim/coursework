package edu.skku.jni;


public class kjh_fpgaTextLCD_JNIDriver {
	static {
		System.loadLibrary("kjh_textlcd_lib");
	}

	public native void on();
	public native void off();
	public native void initialize();
	public native void clear();
	public native void print1Line(String str);
	public native void print2Line(String str);
}
