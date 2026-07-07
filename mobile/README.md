# FaceShield Mobile

This directory contains the independent Android client for FaceShield. It is
kept separate from the Vue web frontend.

Current scope:

- Kotlin Android app skeleton under `android-app/`.
- Jetpack Compose screens for login, permissions, home, records, settings, and result detail.
- Foreground overlay service for the floating scanner button.
- MediaProjection-based one-shot screen capture after explicit user consent.
- Retrofit/OkHttp integration with the existing FastAPI backend.
- DataStore token and backend URL persistence.

Default emulator backend URL:

```text
http://10.0.2.2:8000/
```

Physical Android devices need the backend host machine LAN IP instead.

See `../mobile_design.md` for the detailed design and implementation notes.
