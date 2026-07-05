# FaceShield Database Framework

This folder defines the database framework and conventions only. It does not run migrations or provision an openGauss instance.

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
DATABASE_URL=postgresql+psycopg2://gaussdb:your_password@localhost:5432/faceshield
```

When `DATABASE_URL` is not set, the backend uses a local SQLite development database.

