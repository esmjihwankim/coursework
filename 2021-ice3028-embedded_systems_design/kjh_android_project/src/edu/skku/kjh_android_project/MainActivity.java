package edu.skku.kjh_android_project;

import java.util.ArrayList;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.*;
import android.view.KeyEvent;
import edu.skku.jni.*;


public class MainActivity extends Activity  {
	public static final int musicCount = 10;
	public static final int drumCount = 8; 
	char piano_values[] = { 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x21}; 
	public static int dotState = 0;
	
	kjh_fpgaLED_JNIDriver myLEDDriver = new kjh_fpgaLED_JNIDriver();
	kjh_fpga7segment_JNIDriver my7SegDriver = new kjh_fpga7segment_JNIDriver();
	kjh_fpgaPiezo_JNIDriver myPiezoDriver = new kjh_fpgaPiezo_JNIDriver();
	kjh_fpgaTextLCD_JNIDriver myLcdDriver = new kjh_fpgaTextLCD_JNIDriver();
	static kjh_fpgaDotMatrix_JNIDriver myDotDriver = new kjh_fpgaDotMatrix_JNIDriver();
	
	private ArrayList <String> array_song; 
	private ListView mListView; 
	private MusicListViewAdapter mMusicListViewAdapter;
	private ISoundManager musicManager;
	private ISoundManager drumManager;
	private ImageView imageView; 
	private Button stopMusicButton;
	private Button plusButton;
	private Button minusButton;
	private Button photoSwapButton;
	
	// LED HARDWARE
	static byte[] iLedData = {1,1,1,1,0,0,0,0};
	
	@Override
	protected void onCreate(Bundle savedInstanceState) 
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		setListUI();
		musicManager = new MusicManager(getApplicationContext(), musicCount) ;
		drumManager = new DrumManager(getApplicationContext(), drumCount);
		setImageViewUI();
		setButtonUI();
		myLEDDriver.write(iLedData);
		
		// Dot Thread functions 
		dotState = 1;
		DotThread dotThread = new DotThread();
		dotThread.setPriority(10);
		dotThread.start();
		
	}
	
	@Override
	protected void onPause() {
		myLEDDriver.close();
		super.onPause();
	}
	
	@Override
	protected void onResume() {
		if(myLEDDriver.open("/dev/kjh_fpgaled") < 0)
			Toast.makeText(getApplicationContext(), "LED Driver Open failed", Toast.LENGTH_SHORT).show();
		if(my7SegDriver.open("/dev/kjh_fpga7segment") < 0)
			Toast.makeText(getApplicationContext(), "7Seg Driver Open failed", Toast.LENGTH_SHORT).show();
		
		myLcdDriver.on();
		myPiezoDriver.openPiezo();
		super.onResume();
	
	}
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}
	
	
	TimerTask myTurnPiezoOffTask = new TimerTask(){
		public void run(){
			Log.d("myTask", "PianoPressed");
			myPiezoDriver.writePiezo((char) 0x00);
		}
	};
	
	
	// 16 Keypad Function
	// Orientation:
	// kick1 kick2 kick3 kick4
	// snare1 snare2 snare3 snare4
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		switch(keyCode) {
		case KeyEvent.KEYCODE_1 :
			drumManager.play(R.raw.kick1, 0);
			break;

		case KeyEvent.KEYCODE_2 :
			drumManager.play(R.raw.kick2, 1);
			break;              

		case KeyEvent.KEYCODE_3 :
			drumManager.play(R.raw.kick3, 2);
			break;

		case KeyEvent.KEYCODE_4 :
			drumManager.play(R.raw.kick4, 3);
			break;

		case KeyEvent.KEYCODE_5 :
			drumManager.play(R.raw.snare1, 4);
			break;

		case KeyEvent.KEYCODE_6 :
			drumManager.play(R.raw.snare2, 5);
			break;

		case KeyEvent.KEYCODE_7 :
			drumManager.play(R.raw.snare2, 6);
			break;

		case KeyEvent.KEYCODE_8 :  
			drumManager.play(R.raw.snare2, 7);
			break;
		
		// Piezo (Piano)
		// timer to wait for 0.5 second and then turn off the sound 
		case KeyEvent.KEYCODE_9 :  
			myPiezoDriver.writePiezo(piano_values[0]);
			break;

		case KeyEvent.KEYCODE_0 :  
			myPiezoDriver.writePiezo(piano_values[1]);
			break;
			
		case KeyEvent.KEYCODE_Q :   
			myPiezoDriver.writePiezo(piano_values[2]);
			break;
			
		case KeyEvent.KEYCODE_W :  
			myPiezoDriver.writePiezo(piano_values[3]);
			break;
		}
		
		try{
			Thread.sleep(500);
		}
		catch (InterruptedException e){
			e.printStackTrace();
		}
		myPiezoDriver.writePiezo((char)0x00);
		
		return super.onKeyDown(keyCode, event);
	}
	
	
	
	
	
	
	/////////////////////////// UI Configurations Interface /////////////////////////////////////////
	
	private void pressPlus(){
		for(int i = 0; i <= 7; i++){
			if(iLedData[i]==0){
				iLedData[i] = 1;
				break;
			}
			
		}
		myLEDDriver.write(iLedData);
	}
	
	private void pressMinus(){
		for(int i = 7; i >= 0; i--){
			if(iLedData[i]==1){
				iLedData[i] = 0;
				break;
			}
		}
		myLEDDriver.write(iLedData);
	}
	
	
	void setButtonUI(){
		// Stop Button 
		stopMusicButton = (Button) findViewById(R.id.stopButton);
		stopMusicButton.setOnClickListener(new Button.OnClickListener(){
			@Override
			public void onClick(View view){
				musicManager.stop();
			}
		});
		// + Button 
		plusButton = (Button) findViewById(R.id.plusButton);
		plusButton.setOnClickListener(new Button.OnClickListener(){
			@Override
			public void onClick(View view){
				pressPlus();
			}
		});
		// - Button 
		minusButton = (Button) findViewById(R.id.minusButton);
		minusButton.setOnClickListener(new Button.OnClickListener(){
			@Override
			public void onClick(View view){
				pressMinus();
			}	
		});
		// Photo Swap 
		photoSwapButton = (Button) findViewById(R.id.photoSwapButton);
		photoSwapButton.setOnClickListener(new Button.OnClickListener(){
			@Override
			public void onClick(View view){
				// generate a random number ranging from 1 to 5
				// change picture based on the number 
				final int min = 0;
				final int max = 4;
				final int random = new Random().nextInt(max - min);
				
				switch(random){
					case 0:
						imageView.setImageResource(R.drawable.cartoon);
						break;
					case 1:
						imageView.setImageResource(R.drawable.justin_bieber);
						break;
					case 2:
						imageView.setImageResource(R.drawable.shoes);
						break;
					case 3:
						imageView.setImageResource(R.drawable.simpsonjpg);
						break;
					case 4:
						imageView.setImageResource(R.drawable.univere);
						break;
				}
			}
		});
	}
	
	
	void segmentKeep(int num){
		for(int i = 0; i < 100; i++){
			my7SegDriver.Set_7Segment(num);
		}
	}
	
	void setListUI(){
		mListView = (ListView) findViewById(R.id.musicListView); 
		array_song = new ArrayList<String>();
		array_song.add("bounce");
		array_song.add("childslove");
		array_song.add("cloud9");
		array_song.add("electric");
		array_song.add("flexin");
		array_song.add("idea");
		array_song.add("nonstop");
		array_song.add("realism");
		array_song.add("sauce");
		array_song.add("venom");
		array_song.add("wyn");
		
		// connect adapter
		mMusicListViewAdapter = new MusicListViewAdapter(this, R.layout.layout_song_item, array_song);
		mListView.setAdapter(mMusicListViewAdapter);
		
		// item click listener 
		mListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
			@Override
			public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
				myLcdDriver.clear();
				dotState = 1; 
				switch(position) {
					case 0: 
						musicManager.play(R.raw.bounce, 0); 	
						myLcdDriver.print1Line("bounce");
						segmentKeep(position);
						break;
					case 1: 
						musicManager.play(R.raw.childslove, 0); 
						myLcdDriver.print1Line("childslove");
	
						segmentKeep(position);
						break;
					case 2: 
						musicManager.play(R.raw.cloud9, 0); 
						myLcdDriver.print1Line("cloud9");
						segmentKeep(position);
						break;
					case 3: 
						musicManager.play(R.raw.electric, 0); 
						myLcdDriver.print1Line("electric");
						segmentKeep(position);
						break;
					case 4: 
						musicManager.play(R.raw.flexin, 0);
						myLcdDriver.print1Line("flexin");
						segmentKeep(position);
						break;
					case 5: 
						musicManager.play(R.raw.idea, 0);
						myLcdDriver.print1Line("idea");
						segmentKeep(position);
						break;
					case 6: 
						musicManager.play(R.raw.nonstop, 0);
						myLcdDriver.print1Line("nonstop");
						segmentKeep(position);
						break;
					case 7: 
						musicManager.play(R.raw.realism, 0);
						myLcdDriver.print1Line("realsim");
						segmentKeep(position);
						break;
					case 8: 
						musicManager.play(R.raw.sauce, 0); 
						myLcdDriver.print1Line("sauce");
						segmentKeep(position);
						break;
					case 9: 
						musicManager.play(R.raw.venom, 0); 
						myLcdDriver.print1Line("venom");
						segmentKeep(position);
						break;
					case 10: 
						musicManager.play(R.raw.wyn, 0); 
						myLcdDriver.print1Line("wyn");
						segmentKeep(position);
						break;
				}
			}
			
		});
	}
	
	void setImageViewUI(){
		imageView = (ImageView)findViewById(R.id.imageView);
		imageView.setImageResource(R.drawable.cartoon);
	}
	
	
	public class DotThread extends Thread {
		
		// keyPress = 0 : nothing pressed 
		// keyPress = 1 : kick
		// keyPress = 2 : snare
		public void run(){
			try{
				while(true){
					if(dotState == 0){
						return;
					}
					else {
						myDotDriver.display("DJ Assistant");
					}
				}
			} 
			catch (Exception e) {
				System.out.println(e);
			}
		}

	}

	
	
	

}


