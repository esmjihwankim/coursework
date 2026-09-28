package edu.skku.kjh_android_project;

import android.content.Context;
import android.media.MediaPlayer;

public class MusicManager implements ISoundManager {
	public static MediaPlayer mPlayer[];
	private Context context; 
	private int musicCount;
	
	MusicManager(Context ctx, int count) {
		context = ctx; 
		mPlayer = new MediaPlayer[count];
		musicCount = count;
	}
	
	public void play(int musicID, int index) {
		mPlayer[index] = MediaPlayer.create(context, musicID); 
		mPlayer[index].start();
		mPlayer[index].setLooping(true);
	}

	@Override
	public void stop() {
		for(int i = 0; i < musicCount; i++){
			if(mPlayer[i] != null && mPlayer[i].isPlaying()){
				mPlayer[i].stop();
				mPlayer[i].reset();
			}
		}
	}

	@Override
	public boolean isPlaying() {
		for(int i = 0; i < musicCount; i++){
			if(mPlayer[i].isPlaying() == true) return true; 
		}
		return false;
	}

	@Override
	public void volume() {
		// TODO Auto-generated method stub
		
	} 
	
	
	
	
	
}
