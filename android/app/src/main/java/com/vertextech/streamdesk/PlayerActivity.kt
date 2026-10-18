package com.vertextech.streamdesk

import android.app.Activity
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.*
import android.graphics.Color
import android.content.pm.ActivityInfo
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import androidx.media3.ui.AspectRatioFrameLayout
import androidx.media3.exoplayer.trackselection.DefaultTrackSelector
import androidx.media3.common.TrackSelectionOverride
import androidx.media3.common.TrackGroup
import androidx.media3.common.TrackSelectionParameters

@UnstableApi class PlayerActivity : Activity() {
    private lateinit var player: ExoPlayer; private lateinit var selector: DefaultTrackSelector; private lateinit var pv: PlayerView
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); requestedOrientation=ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE; window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON); window.decorView.systemUiVisibility=(View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or View.SYSTEM_UI_FLAG_LAYOUT_STABLE or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN)
        selector=DefaultTrackSelector(this); player=ExoPlayer.Builder(this).setTrackSelector(selector).build()
        val root=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setBackgroundColor(Color.BLACK) }
        pv=PlayerView(this).apply { useController=true; player= this@PlayerActivity.player; resizeMode=AspectRatioFrameLayout.RESIZE_MODE_FIT; setShowSubtitleButton(true); setControllerAutoShow(true); setShowBuffering(PlayerView.SHOW_BUFFERING_ALWAYS); contentDescription="Video player. Use remote arrows and select for controls." }
        root.addView(pv,LinearLayout.LayoutParams(-1,0,1f))
        val bar=LinearLayout(this).apply { orientation=LinearLayout.HORIZONTAL; gravity=android.view.Gravity.CENTER_VERTICAL; setBackgroundColor(Color.rgb(15,20,32)); setPadding(12,4,12,4) }
        val quality=Spinner(this); val opts=listOf("Auto quality","240p","360p","720p","1080p"); quality.adapter=ArrayAdapter(this,android.R.layout.simple_spinner_dropdown_item,opts); quality.contentDescription="Video quality"; quality.onItemSelectedListener=object: android.widget.AdapterView.OnItemSelectedListener { override fun onNothingSelected(p0:android.widget.AdapterView<*>?){}; override fun onItemSelected(p0:android.widget.AdapterView<*>?,v:View?,position:Int,id:Long){ applyQuality(position) } }; bar.addView(quality)
        val full=Button(this).apply { text="Full screen"; setOnClickListener { window.decorView.systemUiVisibility= (View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or View.SYSTEM_UI_FLAG_LAYOUT_STABLE or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN) } }; bar.addView(full)
        val back=Button(this).apply { text="Back"; setOnClickListener { finish() } }; bar.addView(back); root.addView(bar); setContentView(root)
        val url=intent.getStringExtra("url") ?: ""; title=intent.getStringExtra("title") ?: "StreamDesk Player"
        if(!url.startsWith("https://") && !url.startsWith("http://")) { Toast.makeText(this,"Invalid stream URL",Toast.LENGTH_LONG).show(); finish(); return }
        player.setMediaItem(MediaItem.fromUri(url)); player.prepare(); player.playWhenReady=true
    }
    private fun applyQuality(position:Int) { val b=selector.buildUponParameters(); if(position==0) { b.clearOverrides(); b.setTrackTypeDisabled(androidx.media3.common.C.TRACK_TYPE_VIDEO,false) } else { val height=when(position){1->240;2->360;3->720;else->1080}; b.setMaxVideoSize(Int.MAX_VALUE,height); b.setMinVideoSize(0,0) }; selector.setParameters(b) }
    override fun onStop(){ super.onStop(); if(::player.isInitialized) player.pause() }
    override fun onDestroy(){ if(::player.isInitialized) player.release(); super.onDestroy() }
}