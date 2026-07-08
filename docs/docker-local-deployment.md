# FaceShield Local Docker Deployment

This setup runs the backend on the development machine and exposes it to phones
on the same LAN.

## Start

```powershell
cd D:\BigCreate\FaceShield
.\scripts\docker-local.ps1 up
```

The script prints the backend URL for the phone, for example:

```text
http://192.168.128.204:8000/
```

Use that value in the Android login screen.

## Verify

On the development machine:

```powershell
.\scripts\docker-local.ps1 test
```

On the phone browser:

```text
http://<computer-lan-ip>:8000/api/health
http://<computer-lan-ip>:8000/api/mobile/bootstrap
```

The APK should use the root backend URL:

```text
http://<computer-lan-ip>:8000/
```

## Operate

```powershell
.\scripts\docker-local.ps1 status
.\scripts\docker-local.ps1 logs
.\scripts\docker-local.ps1 restart
.\scripts\docker-local.ps1 down
```

## Use Another Port

```powershell
.\scripts\docker-local.ps1 up -Port 8010
```

The Android backend URL becomes:

```text
http://<computer-lan-ip>:8010/
```

## Data Persistence

Docker named volumes persist SQLite data and generated storage files:

- `faceshield_faceshield-data`
- `faceshield_faceshield-storage`

Stop containers without deleting data:

```powershell
docker compose down
```

Delete all local Docker data for this app:

```powershell
docker compose down -v
```

## Windows Firewall

If the phone cannot open `/api/health`, allow inbound TCP traffic on the backend
port. Run PowerShell as administrator:

```powershell
New-NetFirewallRule -DisplayName "FaceShield Backend 8000" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000
```

## Paddle Mode

The default Docker image is optimized for local mobile integration and runs the
mock algorithm. To run the real Paddle backend, use:

```powershell
.\scripts\docker-local.ps1 up -Paddle
```

If port `8000` is already occupied:

```powershell
.\scripts\docker-local.ps1 up -Paddle -Port 8010
```

Paddle mode mounts the local `model/` directory into the container and points the
backend to:

```text
/app/model/deploy/fusion_v2/best.pdparams
/app/model/deploy/fusion_v2/config.json
```

Verify that the response reports `backend=paddle` and `ready=true`:

```powershell
.\scripts\docker-local.ps1 test -Paddle
```

Keep mock mode for fast UI/network tests. Use Paddle mode when validating real
model inference from the Android app.

## Environment Variables

The following are set in `docker-compose.yml` with demo-safe defaults. Change
`SECRET_KEY` and credentials before any public exposure:

| Variable | Default |
|---|---|
| `SECRET_KEY` | `faceshield-demo-key-2026` |
| `DEMO_USERNAME` | `demo` |
| `DEMO_PASSWORD` | `demo123456` |
| `FACESHIELD_BACKEND_PORT` | `8000` |
| `FACESHIELD_ALGORITHM_BACKEND` | `mock` |

Override in `docker-compose.yml` or via a `.env` file in the project root.
