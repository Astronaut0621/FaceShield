# MySQL Notes

The backend uses SQLAlchemy's MySQL URL form through PyMySQL:

```text
mysql+pymysql://user:password@host:port/database?charset=utf8mb4
```

For the current local development database, use:

```text
mysql+pymysql://faceshield_user:your_password@localhost:3306/faceshield_db?charset=utf8mb4
```

Keep deployment-specific credentials outside source control. Put the real `DATABASE_URL` in a local `.env`, shell environment variable, or deployment secret.
