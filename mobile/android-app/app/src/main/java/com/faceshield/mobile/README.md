# Package Layout

Suggested package responsibilities:

- `auth`: login state, token storage, backend authentication calls.
- `capture`: MediaProjection setup, screenshot capture, frame conversion.
- `detection`: mobile-side detection workflow orchestration.
- `network`: backend API client, request/response DTOs, upload helpers.
- `overlay`: floating window controller and touch interactions.
- `service`: foreground service lifecycle for overlay and capture sessions.
- `ui`: native Android screens such as login, permission guide, settings, result.

