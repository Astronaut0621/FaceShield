# openGauss Notes

The backend uses SQLAlchemy's PostgreSQL-compatible URL form for openGauss:

```text
postgresql+psycopg2://user:password@host:port/database
```

Keep deployment-specific credentials outside source control.

