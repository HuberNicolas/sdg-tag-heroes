
# Alembic Workflow: Commands and Workflow

### Check if DB is Up-to-Date
```bash
alembic current  # Shows current DB revision; no changes to db database
alembic heads    # Shows latest migration revision; no changes to db
```
Compare `current` and `heads` outputs.

### Make a Structural Change
1. Modify your models in code (e.g., add a column).
2. Generate migration:
```bash
alembic revision --autogenerate -m "Describe change"
```
This will generate a `HASH_DESCRIPTION`.py file with all the migrations, we can still modify this

### Apply the Migration to DB
```bash
alembic upgrade head
```
This applies the changes to the db. it will also update the entry in the `alembic_version` database to the newest hash

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
