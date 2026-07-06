# Migrations

Place future ordered migration files here.

Suggested naming:

```text
0001_create_core_tables.sql
0002_add_user_tables.sql
0003_add_model_registry.sql
```

The current prototype uses SQLAlchemy `create_all` in development and `database/sql/001_init_mysql.sql` as the MySQL bootstrap reference.

