# Alembic Migration Setup Summary

## What Was Done

### 1. Initialized Alembic
- Created `alembic/` directory structure
- Generated `alembic.ini` configuration file
- Created `alembic/env.py` with async/sync compatibility

### 2. Configured Environment (`alembic/env.py`)
- Uses **synchronous** SQLAlchemy engine for migrations (works reliably with SQLite)
- Automatically imports all models for autogenerate support
- Converts async database URL (`sqlite+aiosqlite://`) to sync format for migrations
- Works with both Docker and development environments

### 3. Created Initial Migration
- **Revision ID**: `981cbaae32a1`
- **File**: `alembic/versions/981cbaae32a1_initial_migration_creating_all_tables.py`
- Creates all tables:
  - `accounts`
  - `servers`
  - `bindings`
  - `transactions`
  - `transaction_snapshots`
  - All indexes and foreign keys
  - Enum types for statuses

### 4. Updated Application Startup (`backend/app/main.py`)
- Replaced `create_tables()` call with automatic migration runner
- Migrations run on every application startup using subprocess
- Logs migration success/failure appropriately
- Fallback to `create_tables()` removed from main.py

### 5. Updated Documentation
- Created `alembic/README.md` with:
  - Migration usage commands
  - Workflow examples
  - Troubleshooting guide
  - Best practices
- Added `.gitignore` entries for database files

## How It Works

### Development Workflow
```bash
# 1. Modify models in backend/app/models/
# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# 3. Review migration in alembic/versions/
# 4. Restart application (migrations run automatically)
# Database is updated!
```

### Production Workflow
```bash
# In Docker container:
# - Database at /app/application.db (volume mounted)
# - Migrations run automatically on startup
# - Same migration files work identically
```

## Key Features

### ✅ Automatic Migrations
- No manual migration commands needed during development
- Runs on every application startup
- Applies only pending migrations

### ✅ Version Control
- All schema changes tracked in git
- Team collaboration friendly
- Rollback support built-in

### ✅ Docker Compatible
- Works in both Docker and development
- Database path handled automatically
- Same migrations, different environments

### ✅ Type Safe
- Autogenerate detects model changes
- Indexes and constraints included
- Enum types handled correctly

## Configuration Files

### `backend/alembic.ini`
- Alembic configuration
- Script location: `alembic/`
- Database URL: Loaded from `app.core.settings` (not hardcoded)

### `backend/alembic/env.py`
- Imports all models for autogenerate
- Converts async URL to sync format
- Runs migrations online (with database connection)

### `backend/alembic/versions/`
- Contains migration files
- One file per schema change
- Naming: `{revision}_{description}.py`

## Database URLs

### Development
```
DB__DB_URL = sqlite+aiosqlite:///./application.db
```
- File: `./application.db` in project root
- Relative to current working directory
- **Important**: Migrations must run from project root to hit this database

### Docker
```yaml
volumes:
  - ./application.db:/app/application.db
```
- File: `/app/application.db` (in container)
- Mounted to project root as `./application.db`

### Important: Multiple Database Files
**Common mistake**: Running `alembic` commands from `backend/` directory creates/migrates `backend/application.db`, but the app uses `./application.db` (project root).

**Always run migrations from project root**:
```bash
# From project root, NOT backend/
cd D:\dev-personal\idvkit\mkit-idv-next

# Use explicit config path
python -m alembic -c backend/alembic.ini upgrade head
```

The `main.py` lifespan function handles this correctly by:
1. Finding project root (parent of backend/)
2. Using explicit alembic.ini path
3. Running from correct working directory

## Migration Commands Reference

```bash
# View current version
alembic current

# View migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show SQL (dry run)
alembic upgrade head --sql
```

## Troubleshooting

### Migration conflicts
```bash
# If autogenerate detects conflicts:
alembic revision -m "Manual resolution"
# Edit the generated file manually
alembic upgrade head
```

### Reset database (development only)
```bash
# Stop application
rm backend/application.db
# Start application (migrations will recreate everything)
```

### Check migration status
```bash
cd backend
alembic current
# Shows: 981cbaae32a1 (or current revision)
```

## Best Practices

1. **Always review migrations** before committing
2. **Write clear descriptions** - future you will thank current you
3. **Test in development** before deploying
4. **Never modify applied migrations** - create new ones
5. **Keep migrations atomic** - one logical change per file

## Migration from create_tables()

### Before (old way):
```python
# main.py
from app.database.tables import create_tables

async def lifespan(app):
    await create_tables()
```

### After (new way):
```python
# main.py
# Migrations run automatically via subprocess
# No manual intervention needed
```

## File Changes Summary

| File | Change |
|------|--------|
| `backend/app/main.py` | Removed `create_tables()` import, added migration runner |
| `backend/app/database/tables.py` | Added note about migrations being preferred |
| `backend/alembic/` | **New directory** - Alembic configuration |
| `backend/alembic/env.py` | **New file** - Migration environment |
| `backend/alembic/versions/981cbaae32a1_*.py` | **New file** - Initial migration |
| `backend/alembic/README.md` | **New file** - Migration documentation |
| `.gitignore` | Added database file patterns |

## Testing

To verify migrations work:

```bash
cd backend
python -c "from app.main import app; print('OK')"
# Should print: OK without errors

# Check database exists
ls application.db
# Should show: application.db file

# Check alembic version table
sqlite3 application.db "SELECT * FROM alembic_version"
# Should show: 981cbaae32a1 row
```

## Next Steps

1. Review the initial migration file
2. Test application startup
3. Verify all tables created correctly
4. Update documentation as needed

## Support

For issues or questions:
- Check `backend/alembic/README.md`
- Review Alembic documentation: https://alembic.sqlalchemy.org/
- Check logs in `backend/logs/`
