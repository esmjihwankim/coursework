package edu.skku.sms;

import edu.skku.sms_jni.PiezoJNI;
import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.Menu;
import android.widget.TextView;

public class MainActivity extends Activity {
    private TextView text;
    private PiezoJNI piezoJNI = new PiezoJNI();
    char values[] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x21};
    
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
	
      
        text = (TextView) findViewById(R.id.textView1);
	}
	
    @Override
    public void onResume() {
        piezoJNI.open();
    	super.onResume();
    }

    @Override
    public void onPause() {
    	piezoJNI.close();
    	super.onPause();
    }
		

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

	public boolean onKeyDown(int keyCode, KeyEvent event) {
		switch(keyCode) {
		case KeyEvent.KEYCODE_1 :
			piezoJNI.write((char)0);
			text.setText("#\n"); break;

		case KeyEvent.KEYCODE_2 :
			piezoJNI.write(values[0]);
			text.setText("도\n"); break;                              

		case KeyEvent.KEYCODE_3 :
			piezoJNI.write(values[1]);
			text.setText("레\n"); break;

		case KeyEvent.KEYCODE_4 :
			piezoJNI.write(values[2]);
			text.setText("미\n"); break;

		case KeyEvent.KEYCODE_5 :
			piezoJNI.write(values[3]);
			text.setText("파\n"); break;

		case KeyEvent.KEYCODE_6 :
			piezoJNI.write(values[4]);
			text.setText("솔\n"); break;

		case KeyEvent.KEYCODE_7 :
			piezoJNI.write(values[5]);
			text.setText("라\n"); break;

		case KeyEvent.KEYCODE_8 :
			piezoJNI.write(values[6]);
			text.setText("시\n"); break;
			
		case KeyEvent.KEYCODE_9 :
			piezoJNI.write(values[7]);
			text.setText("도\n"); break;

		case KeyEvent.KEYCODE_0 :
			piezoJNI.write(values[8]);
			text.setText("레\n"); break;
			
		case KeyEvent.KEYCODE_Q :
			piezoJNI.write(values[9]);
			text.setText("미\n"); break;
			
		case KeyEvent.KEYCODE_W :
			piezoJNI.write(values[10]);
			text.setText("파\n"); break;
			
		case KeyEvent.KEYCODE_E :
			piezoJNI.write(values[11]);
			text.setText("솔\n"); break;
			
		case KeyEvent.KEYCODE_R :
			piezoJNI.write(values[12]);
			text.setText("라\n"); break;
			
		case KeyEvent.KEYCODE_T :
			piezoJNI.write(values[13]);
			text.setText("시\n"); break;
			
		case KeyEvent.KEYCODE_Y :
			piezoJNI.write(values[14]);
			text.setText("도\n"); break;
			
		}

		return super.onKeyDown(keyCode, event);
	}

}
