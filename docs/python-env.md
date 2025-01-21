
# Environment Setup and TypeScript Schema Generation

Instructions for managing the `api` and `pipeline` environments and generating TypeScript schemas.

## Conda Environments

### List Available Environments
To see all available environments, run:
```bash
conda env list
```

### Activate the Environments
- For `api`:
  ```bash
  conda activate p-3.10.14-mt-igcl
  ```

- For `pipeline`:
  ```bash
  conda activate p-3.10.14-mt-pipeline
  ```

## Poetry Commands

### Install Dependencies
Run the following in the active environment to install dependencies:
```bash
poetry install --no-root
```

### Add a New Package
To add a package, use:
```bash
poetry add <PACKAGE_NAME>
```

### Manually Update Dependencies
If you manually add dependencies to the `pyproject.toml` file, lock the dependencies with:
```bash
poetry lock
```
