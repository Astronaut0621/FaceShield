# Capture Module

Future responsibilities:

- Request MediaProjection permission through a visible user consent flow.
- Create `VirtualDisplay` and `ImageReader` for screenshot capture.
- Capture only when the user taps the floating window action.
- Convert the captured frame to JPEG or PNG before upload.
- Release projection resources when the foreground service stops.

Important: Android does not allow silent cross-app screenshots. The app must
obtain explicit MediaProjection consent from the user.

