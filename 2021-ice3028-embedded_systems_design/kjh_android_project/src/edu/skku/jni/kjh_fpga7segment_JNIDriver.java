package edu.skku.jni;

public class kjh_fpga7segment_JNIDriver {
	private boolean mConnectFlag;

	static {
		System.loadLibrary("kjh_7segment_lib");
	}

	private native static int open7Driver(String path);
	private native static void close7Driver();
	private native static void write7Driver(int value);
	private native static void ioctl7Driver(int value);

	public kjh_fpga7segment_JNIDriver() {
		mConnectFlag = false;
	}

	public int open(String driver) {
		if (mConnectFlag)
			return -1;
		
		if(open7Driver(driver) > 0) {
			mConnectFlag = true;
			return 1;
		}
		else 
			return -2;
	}
	
	public void close() {
		if (!mConnectFlag)
			return;
		mConnectFlag = false;
		close7Driver();
	}

	public void SegmentControl(int value) {
		if (!mConnectFlag)
			return;
		write7Driver(value);
	}

	public void SegmentIOControl(int value) {
		if (!mConnectFlag)
			return;
		ioctl7Driver(value);
	}

	protected void finalize() throws Throwable{
		close();
		super.finalize();
	}
	
	public void Set_7Segment(int data) {
		if (!mConnectFlag)
			return;
		write7Driver(data);
	}
	
		
}
