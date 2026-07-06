# FaceShield Database Framework

This folder defines the database framework and conventions only. It does not run migrations or provision a MySQL instance.

## Structure

```text
sql/         Hand-written SQL snapshots or bootstrap scripts
migrations/ Future migration files
seeds/      Future seed data
schemas/    Logical schema documentation
docs/       Database operation notes
scripts/    Placeholder scripts for future migration automation
```

## Runtime Configuration

The backend reads `DATABASE_URL`.

```text
DATABASE_URL=mysql+pymysql://faceshield_user:your_password@localhost:3306/faceshield_db?charset=utf8mb4
```

When `DATABASE_URL` is not set, the backend uses a local SQLite development database.

