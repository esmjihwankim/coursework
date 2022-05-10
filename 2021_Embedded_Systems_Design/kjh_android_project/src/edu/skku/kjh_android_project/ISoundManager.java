package edu.skku.kjh_android_project;

public interface ISoundManager {
	void play(int musicID, int index);
	void stop();
	boolean isPlaying();
	void volume();
}
