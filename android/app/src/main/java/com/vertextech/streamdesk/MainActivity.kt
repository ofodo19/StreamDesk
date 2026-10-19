package com.vertextech.streamdesk

import android.app.Activity
import android.os.Bundle
import android.graphics.Color
import android.view.View
import android.view.Gravity
import android.widget.*
import android.content.Intent
import org.json.JSONObject
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : Activity() {
    // Android emulator reaches the Windows host at 10.0.2.2. Change this for a deployed HTTPS API.
    private val apiBase = "https://ofodo.pythonanywhere.com"
    private lateinit var list: LinearLayout
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); window.statusBarColor=Color.rgb(8,13,24); window.navigationBarColor=Color.rgb(8,13,24); buildUi() }
    override fun onResume() { super.onResume(); if (::list.isInitialized) loadCatalogue() }
    private fun buildUi() {
        val scroll=ScrollView(this); val page=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(28,28,28,28); setBackgroundColor(Color.rgb(8,13,24)) }
        page.addView(TextView(this).apply { text="STREAMDESK"; textSize=28f; setTextColor(Color.WHITE); setTypeface(null,1) })
        page.addView(TextView(this).apply { text="Live channels · Android & Android TV"; textSize=16f; setTextColor(Color.LTGRAY); setPadding(0,4,0,20) })
        val refresh=Button(this).apply { text="Refresh playlists"; setOnClickListener { loadCatalogue() } }; page.addView(refresh)
        list=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; setPadding(0,18,0,0) }; page.addView(list); scroll.addView(page); setContentView(scroll)
    }
    private fun loadCatalogue() { list.removeAllViews(); list.addView(TextView(this).apply { text="Loading published channels…"; textSize=18f; setTextColor(Color.WHITE) })
        thread { try { val c=URL("$apiBase/api/catalogue?ts=${System.currentTimeMillis()}").openConnection() as HttpURLConnection; c.connectTimeout=15000; c.readTimeout=20000; c.setRequestProperty("Cache-Control","no-cache"); val data=JSONObject(c.inputStream.bufferedReader().use { it.readText() }); val pls=data.optJSONArray("playlists") ?: JSONArray(); runOnUiThread { list.removeAllViews(); if(pls.length()==0) list.addView(TextView(this).apply { text="No published playlists yet. Publish an authorized playlist from the admin API."; setTextColor(Color.LTGRAY); textSize=17f }) else for(i in 0 until pls.length()) { val p=pls.getJSONObject(i); val channels=p.optJSONArray("channels") ?: JSONArray(); list.addView(TextView(this).apply { text=p.optString("name","Playlist")+" · ${channels.length()} channels"; textSize=20f; setTextColor(Color.WHITE); setPadding(0,18,0,8) }); for(j in 0 until channels.length()) { val ch=channels.getJSONObject(j); val b=Button(this).apply { text=ch.optString("name","Channel"); textSize=16f; setOnClickListener { startActivity(Intent(this@MainActivity,PlayerActivity::class.java).putExtra("url",ch.optString("url")).putExtra("title",ch.optString("name"))) } }; list.addView(b) } } } } catch(e:Exception) { runOnUiThread { list.removeAllViews(); list.addView(TextView(this).apply { text="Cannot connect to the StreamDesk cloud catalogue at $apiBase. Check your internet connection and retry."; setTextColor(Color.YELLOW); textSize=16f }) } } }
    }
}