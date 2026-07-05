# FaceShield Frontend

Minimal Vue 3 + Vite frontend scaffold for FaceShield.

## Run

```bash
npm install
npm run dev
```

## Structure

```text
src/api/          Backward-compatible API exports
src/config/       App-level runtime config
src/constants/    Route and shared constants
src/layouts/      Application shell layouts
src/services/     HTTP client and cross-feature services
src/stores/       Lightweight reactive stores
src/composables/  Reusable Vue composition utilities
src/shared/       Shared UI components
src/features/     Feature modules grouped by domain
src/views/        Route-level page components
src/utils/        Formatting and response helpers
```

Feature modules should own their own components and service wrappers. Route pages should compose feature modules instead of embedding business details directly.

## Demo Login

The default backend seeds a demo account:

```text
username: demo
password: demo123456
```

The frontend stores the bearer token in `localStorage` for the MVP demo and attaches it to protected API calls.
