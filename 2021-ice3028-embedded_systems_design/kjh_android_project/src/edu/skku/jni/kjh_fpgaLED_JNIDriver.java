package edu.skku.jni;

public class kjh_fpgaLED_JNIDriver {
	private boolean mConnectFlag;

	static {
		System.loadLibrary("kjh_led_lib");
	}
		
	private native static int openLEDDriver(String path);
	private native static void closeLEDDriver();
	private native static void writeLEDDriver(byte[] data, int length);

	public kjh_fpgaLED_JNIDriver(){
		mConnectFlag = false;
	}

	public int open(String driver){
		if(mConnectFlag) return -1;

		if(openLEDDriver(driver)>0){
			mConnectFlag = true;
			return 1;
		} else {
			return -1;
		}
	}

	public void close(){
		if(!mConnectFlag) return;
		mConnectFlag = false;
		closeLEDDriver();
	}

	protected void finalize() throws Throwable{
		close();
		super.finalize();
	}

	public void write(byte[] data){
		if(!mConnectFlag) return;
		writeLEDDriver(data, data.length);
	}
}
