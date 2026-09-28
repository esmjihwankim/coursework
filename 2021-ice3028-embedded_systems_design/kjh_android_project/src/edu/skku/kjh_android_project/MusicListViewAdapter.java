package edu.skku.kjh_android_project;

import java.util.ArrayList;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ListView;
import android.widget.ListAdapter;
import android.widget.BaseAdapter;
import android.widget.TextView;


public class MusicListViewAdapter extends BaseAdapter {
	private Context mContext; 
	private ArrayList<String> array_songs; 
	int mResource; 
	
	// Constructor 
	public MusicListViewAdapter(Context mContext, int resource, ArrayList<String> array_songs){
		this.mContext = mContext;
		this.mResource = resource;
		this.array_songs = array_songs;
	}
	
	
	@Override
	public int getCount() {
		return array_songs.size();
	}
	
	@Override
	public Object getItem(int position) {
		return array_songs.get(position);
	}
	
	@Override
	public long getItemId(int position) {
		return position; 
	}
	
	@Override
	public View getView(int position, View convertView, ViewGroup parent) {
		View v = convertView;
		
		LayoutInflater inflater = LayoutInflater.from(mContext);
		convertView = inflater.inflate(R.layout.layout_song_item, parent, false);
		
		TextView textView =(TextView)convertView.findViewById(R.id.song_name_txt); 
		
		textView.setText(array_songs.get(position));
		return convertView;
	}
	

}

