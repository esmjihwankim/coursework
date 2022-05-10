package edu.skku.sms_jni;

public class PiezoJNI {
	static {
		System.loadLibrary("PiezoJNI");
	}

	public native void open();
	public native void write(char data);
	public native void close();
}
