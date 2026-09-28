package edu.skku.kjh_android_project;

import android.content.Context;
import android.media.MediaPlayer;

public class DrumManager implements ISoundManager {
	// Drums should not loop 
	public static MediaPlayer mPlayer[];
	private Context context; 
	private int drumCount;
	
	
	DrumManager(Context ctx, int count)
	{
		context = ctx; 
		mPlayer = new MediaPlayer[count];
		drumCount = count;
	}
	
	
	@Override
	public void play(int musicID, int index) {
		mPlayer[index] = MediaPlayer.create(context, musicID); 
		mPlayer[index].start();
		mPlayer[index].setLooping(false);
	}

	@Override
	public void stop() {
		
	}

	@Override
	public boolean isPlaying() {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void volume() {
		// TODO Auto-generated method stub
	}

}
