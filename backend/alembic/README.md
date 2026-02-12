# Alembic Migrations

This directory contains database migration files for the application.

## What are Migrations?

Migrations allow you to track and apply schema changes to your database in a version-controlled way. Instead of using `create_tables()`, migrations provide:

- **Version control**: Track all schema changes over time
- **Team collaboration**: Share schema changes across developers
- **Rollback support**: Revert changes if needed
- **Production safety**: Preview and test changes before applying

## Automatic Migrations

Migrations run **automatically** on application startup via `main.py`. You don't need to run them manually during normal development.

## Manual Migration Commands

### Create a New Migration

```bash
# From backend directory
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Show current version
alembic current
```

### Rollback Migrations

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### View Migration History

```bash
# Show all migrations
alembic history

# Show SQL for a migration (without executing)
alembic upgrade head --sql
```

## Docker & Development

Migrations work identically in both environments:

- **Docker**: Database at `/app/application.db` (mounted volume)
- **Development**: Database at `./application.db` (project root)

Both use SQLite with the same schema, so migrations are portable across environments.

## Troubleshooting

### Migration Conflicts

If autogenerate detects conflicts:

```bash
# Create migration with manual merge
alembic revision -m "Manual description"

# Edit the generated file in alembic/versions/
# Then apply: alembic upgrade head
```

### Reset Database (Development Only)

```bash
# Delete database and re-run migrations
rm application.db
alembic upgrade head
```

### Fresh Start

To completely reset your database:

1. Stop the application
2. Delete `application.db` (backend directory)
3. Start application (migrations will run automatically)

## Best Practices

1. **Always create migrations** after model changes
2. **Write clear descriptions** in migration messages
3. **Review generated SQL** before committing
4. **Test in development** before deploying to production
5. **Never modify applied migrations** - create new ones instead

## Model Change Workflow

1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "..."`
3. Review generated migration file
4. Restart application (migrations auto-apply)
5. Verify changes in development

## Important Notes

- Migrations use **synchronous** SQLAlchemy engine (not async)
- Database URL is automatically converted from `+aiosqlite` to sync format
- The `alembic_version` table tracks applied migrations
- All migrations run in **online mode** with actual database connection
