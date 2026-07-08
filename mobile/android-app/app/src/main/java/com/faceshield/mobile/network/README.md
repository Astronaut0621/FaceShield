# Network Module

Future responsibilities:

- Configure backend base URL.
- Add `Authorization: Bearer <token>` to protected requests.
- Upload captured screenshots as multipart files.
- Parse the existing backend response envelope:

```json
{
  "code": 200,
  "message": "Detection completed.",
  "data": {}
}
```

