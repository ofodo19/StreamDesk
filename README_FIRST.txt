STREAMDESK FULL STARTER PACKAGE

Contains:
1) android/ — native Kotlin Android phone + Android TV app source using Media3/ExoPlayer.
2) backend/ — local API with catalogue endpoint and explicit draft -> publish workflow.
3) This is source code, not a compiled APK.

WINDOWS BACKEND QUICK START
1. Install Python 3.10+.
2. Open Command Prompt in the backend folder.
3. Run: python streamdesk_server.py
4. Open http://127.0.0.1:8787/api/health

ANDROID BUILD
1. Install Android Studio.
2. Open the android folder.
3. Let Gradle sync.
4. Build > Build APK(s).

PUBLISHING
The API provides POST /api/drafts and POST /api/publish. Publishing requires confirm_rights=true. This starter does not auto-publish unreviewed third-party scrape results. Add authentication before deploying to a shared server.
