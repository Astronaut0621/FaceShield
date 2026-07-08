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

This repository includes the Gradle wrapper. Command-line builds use:

```bash
./gradlew :app:assembleDebug
```

If you run the backend on the development machine and test with the Android
emulator, use:

```text
http://10.0.2.2:8000/
```

For a physical Android phone, `10.0.2.2` will not work because it is an emulator
alias. Start the backend on all network interfaces:

```bash
cd backend
python run.py
```

Then find the development machine's LAN IP address, make sure the phone is on
the same Wi-Fi network, and enter this URL on the login screen:

```text
http://<your-computer-lan-ip>:8000/
```

On Windows, allow Python or port `8000` through the firewall if the phone still
cannot reach the backend.

## Local Docker backend over LAN

From the repository root:

```bash
docker compose up -d --build
```

Verify the backend on the development machine:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/mobile/bootstrap
```

Then use the development machine's LAN IP address on the phone:

```text
http://<your-computer-lan-ip>:8000/
```

The Android login flow probes `/api/mobile/bootstrap` before login, so a
reachable but incompatible backend will fail before credentials are submitted.
