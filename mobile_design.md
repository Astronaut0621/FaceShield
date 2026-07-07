# FaceShield Mobile Design

## 1. Goal

This document describes the independent Android mobile client for FaceShield.
The mobile app must stay separate from the Vue web frontend. All mobile code
belongs under `mobile/`.

Target user flow:

1. The user opens the FaceShield Android app.
2. The app guides the user through login, backend URL setup, overlay permission,
   notification permission, and screen-capture consent.
3. The app starts a foreground service and shows a draggable floating button.
4. During a WeChat video call, the user taps the floating button.
5. The app captures the current screen through Android MediaProjection.
6. The screenshot is uploaded to the existing backend detection API.
7. The app shows whether the visible face has low, medium, or high AI-forgery risk.

Important boundary:

- Android does not allow silent cross-app screenshots.
- Screen capture must use MediaProjection and explicit user consent.
- If Android, WeChat, a device ROM, DRM, or `FLAG_SECURE` blocks capture, the app
  must show a failure state and must not bypass the platform restriction.
- The app should capture only after a user tap, not continuously in the background.

## 2. Current Mobile Structure

```text
mobile/
  README.md
  android-app/
    settings.gradle.kts
    build.gradle.kts
    gradle.properties
    app/
      build.gradle.kts
      src/main/
        AndroidManifest.xml
        java/com/faceshield/mobile/
          MainActivity.kt
          FaceShieldApp.kt
          auth/
          capture/
          detection/
          model/
          network/
          overlay/
          service/
          ui/
        res/
  docs/
  test-plan/
```

Module responsibilities:

- `auth`: login, token storage, current user session.
- `network`: Retrofit API client, Bearer token injection, backend DTOs.
- `capture`: MediaProjection authorization state and screenshot capture.
- `overlay`: floating window rendering, drag, tap, and long-press handling.
- `service`: foreground service lifecycle for overlay and capture workflow.
- `detection`: capture-upload-detect orchestration.
- `ui`: Compose screens for login, permissions, home, settings, records, result.
- `model`: app state, DTOs, and domain models.

## 3. Recommended Android Stack

- Kotlin
- Android native app
- Jetpack Compose
- Foreground Service
- MediaProjection API
- WindowManager overlay with `TYPE_APPLICATION_OVERLAY`
- Retrofit + OkHttp
- Jetpack DataStore
- Kotlin Coroutines and Flow

Do not implement this as a WebView wrapper. The required overlay, foreground
service, and screen-capture behavior are native Android responsibilities.

## 4. Required Permissions

Manifest-level permissions:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

MediaProjection is not granted through a normal manifest permission. It must be
requested by launching the Android screen-capture consent activity.

Recommended permission order:

1. Login and backend URL setup.
2. Request notification permission on Android 13+.
3. Open system settings for floating-window permission.
4. Start the foreground service.
5. Request MediaProjection consent when the first scan is needed.

## 5. Backend Integration

The MVP can reuse the current backend.

Login:

```text
POST /api/auth/login
Content-Type: application/json
```

Request:

```json
{
  "username": "demo",
  "password": "demo123456"
}
```

Detection:

```text
POST /api/detect
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
file=<screenshot.jpg>
```

Record detail:

```text
GET /api/records/{task_id}
Authorization: Bearer <access_token>
```

The Android DTOs must map backend snake_case fields with `@SerializedName`, for
example `access_token`, `fake_probability`, `risk_level`, and `face_detected`.

## 6. Foreground Service and Overlay

The floating scanner should be owned by a foreground service:

```text
MainActivity
-> permission guide
-> start FaceShieldOverlayService
-> OverlayView.show()
-> tap floating button
-> request/consume MediaProjection
-> capture screenshot
-> upload to backend
-> update overlay state
```

Overlay states:

```text
IDLE
PERMISSION_REQUIRED
CAPTURING
UPLOADING
DETECTING
SUCCESS_LOW
SUCCESS_MEDIUM
SUCCESS_HIGH
FAILURE
```

UX requirements:

- The button must be small and draggable.
- Tapping triggers one scan.
- Long-pressing stops protection.
- Repeated taps must not create concurrent uploads.
- The foreground notification must provide a stop action.

## 7. Capture Rules

The capture module should:

- Use MediaProjection only after explicit consent.
- Capture one frame after the user taps the overlay.
- Convert the frame to a cropped Bitmap without row-padding artifacts.
- Resize the image to a reasonable maximum edge, such as 1440 px.
- Compress to JPEG before upload.
- Delete the temporary screenshot after upload.

If capture returns an empty frame or the platform blocks capture, show a clear
failure state.

## 8. Android 14 Note

The overlay service declares both `specialUse` and `mediaProjection` foreground
service types. Start the long-running floating control with `specialUse`, then
promote the service with `mediaProjection` only after the user grants Android
screen-capture consent. This avoids Android 14 foreground-service type failures
while still keeping the overlay lifecycle separate from capture.

The development network security config permits cleartext HTTP so a physical
phone can connect to a LAN backend such as `http://192.168.x.x:8000/`. Production
builds should use HTTPS and tighten this policy.

## 9. MVP Milestones

1. Compile the Android project in Android Studio.
2. Sign in against the local FastAPI backend.
3. Grant overlay and notification permissions.
4. Start the foreground service and show the floating button.
5. Request MediaProjection consent.
6. Capture a test screen.
7. Upload the screenshot to `/api/detect`.
8. Show low, medium, high, or failure state on the overlay.
9. Verify the backend history contains the mobile detection record.

## 10. Implementation Notes From Static Review

- `MainActivity` uses `singleTop` and handles a service-launched action to request
  MediaProjection consent. This keeps the floating button flow usable while the
  user is inside another app.
- After MediaProjection consent succeeds, `MainActivity` starts the overlay
  service with `ACTION_MEDIA_PROJECTION_READY` so the service can consume the
  pending authorization result.
- The Retrofit DTOs must remain protected by ProGuard/R8 keep rules because Gson
  relies on their field names and annotations.
- Release builds should not log HTTP bodies. Debug builds may keep OkHttp body
  logging for local API inspection.
- The default emulator backend URL is `http://10.0.2.2:8000/`. Physical devices
  need the host machine LAN IP instead.

## 11. Test Plan

Test on at least:

- Android emulator for login and backend API integration.
- One Android 13+ physical device for notification permission.
- One Android 14 device for foreground service behavior.
- One domestic Android ROM if available, because overlay permissions vary.

Manual WeChat video-call checks:

- Overlay is visible during the call.
- Tap captures only after user consent.
- Capture failure is handled cleanly.
- Upload timeout and offline states are visible.
- Long press stops the overlay service.
