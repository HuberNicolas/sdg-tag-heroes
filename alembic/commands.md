
# Alembic Workflow: Commands and Workflow

```

### Make a Structural Change
1. Modify your models in code (e.g., add a column).
2. Generate migration:
```bash
alembic revision --autogenerate -m "Describe change"
```

### Apply the Migration to DB
```bash
alembic upgrade head
```

### Check if DB is Up-to-Date
```bash
alembic current  # Shows current DB revision
alembic heads    # Shows latest migration revision
```
Compare `current` and `heads` outputs.

### Rollback a Migration
#### Go down one migration:
```bash
alembic downgrade -1
```

#### Go to a specific revision:
```bash
alembic downgrade <revision_id>
```

#### Go back to the latest migration:
```bash
alembic upgrade head
```
