# FaceShield Android App

Native Android client for FaceShield.

## Modules

- `auth`: login state, token storage, user session.
- `capture`: MediaProjection state and screenshot capture.
- `detection`: capture/upload/detection workflow orchestration.
- `network`: Retrofit API client and backend DTOs.
- `overlay`: floating window rendering and interaction.
- `service`: foreground service for the floating protection workflow.
- `ui`: Compose screens.

## Build

Open this directory in Android Studio and let it sync Gradle.

This repository currently has Gradle wrapper properties, but no checked-in
`gradlew`, `gradlew.bat`, or wrapper jar. Generate or restore the wrapper before
command-line builds:

```bash
gradle wrapper
./gradlew :app:assembleDebug
```

If you run the backend on the development machine and test with the Android
emulator, use:

```text
http://10.0.2.2:8000/
```
