# Core Tables

Initial logical schema:

- `users`: demo login users and account status.
- `file_record`: uploaded file metadata.
- `detection_task`: detection task lifecycle.
- `detection_result`: model result payload.
- `model_version`: model metadata and active version marker.
- `detection_records`: openGauss view aligning with the development spec record naming.

The canonical SQL snapshot is `database/sql/001_init_opengauss.sql`.
