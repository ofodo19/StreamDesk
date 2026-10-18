# StreamDesk Android app (source project)

This is a native Kotlin Android starter for phones and Android TV, using AndroidX Media3/ExoPlayer with HLS support, fullscreen playback, remote-friendly buttons, and quality caps.

## Build APK in Android Studio
1. Install Android Studio (current stable) and its Android SDK 35 / JDK 17.
2. Open the `android` folder in Android Studio.
3. Let Gradle sync and resolve Media3 dependencies.
4. Use **Build → Build Bundle(s) / APK(s) → Build APK(s)**.
5. Install `app/build/outputs/apk/debug/app-debug.apk` on a test device.

## Backend URL
`MainActivity.kt` defaults to `http://10.0.2.2:8787`, which is the host computer from the Android emulator. For a real Android phone/TV, change `apiBase` to your computer's LAN IP (e.g. `http://192.168.1.10:8787`) or, for production, an HTTPS backend URL. Ensure the device can reach the server.

## Quality behavior
Auto lets ExoPlayer adapt to HLS variant streams. Manual options cap maximum video height at 240/360/720/1080p. The source must expose variants for actual quality changes; a single fixed-quality URL cannot be converted into multiple qualities by the player. This starter expects direct, authorized media URLs, ideally `.m3u8` HLS streams. It does not resolve webpages into streams.

## Important demo limitations
- This is Android source code, not a precompiled APK. Build it with Android Studio.
- The demo API has no admin login, HTTPS, database, or deployment hardening. Do not expose it publicly.
- Only publish streams you own or are licensed to redistribute. The publish endpoint requires an explicit rights confirmation.
