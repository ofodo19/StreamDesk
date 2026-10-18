# StreamDesk demo API

This API supports a published catalogue for the Android player and a review/publish workflow. It deliberately does not scrape third-party streaming sites or resolve hidden media URLs.

## Windows
```bat
cd /d path\to\streamdesk_full\backend
python streamdesk_server.py
```
Check `http://127.0.0.1:8787/api/health`.

## API
- `GET /api/catalogue` — published playlists for the app.
- `POST /api/drafts` — save `{ "name": "My playlist", "channels": [{"name":"Channel 1","url":"https://your-authorized-stream.m3u8","type":"hls"}] }`.
- `POST /api/publish` — publish latest draft with `{ "confirm_rights": true }` after confirming distribution rights.

This demo server has no admin authentication. Keep it local or add authentication and HTTPS before network deployment. Published JSON is stored in `data/catalogue.json`.
