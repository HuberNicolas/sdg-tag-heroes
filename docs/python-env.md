# Python environments

There are two Poetry projects, both for Python 3.10.14:

| Project                                          | Used for                                                                 |
|--------------------------------------------------|--------------------------------------------------------------------------|
| [`pipeline/pyproject.toml`](../pipeline/pyproject.toml) | All dataset scripts on your machine: pipeline, UMAP, BERTopic, loaders, fixtures, Alembic |
| [`api/pyproject.toml`](../api/pyproject.toml)           | The API container (`deploy/api.Dockerfile`)                              |

## Set up the scripts environment

Run from the repository root:

```bash
poetry -C pipeline env use python3.10
```

```bash
poetry -C pipeline install --no-root
```

```bash
source "$(poetry -C pipeline env info --path)/bin/activate"
```

If `python3.10` is not Python 3.10.14, install that version, for example with [uv](https://docs.astral.sh/uv/):

```bash
uv python install 3.10.14
```

and pass the path from `uv python find 3.10.14` to `poetry -C pipeline env use`.

## Poetry commands

Add a package:

```bash
poetry -C pipeline add <PACKAGE_NAME>
```

After editing `pyproject.toml` by hand, update the lock file without upgrading other packages:

```bash
poetry -C pipeline lock --no-update
```
