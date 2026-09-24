# Development

Setting up the Python environment, linting and formatting, and the conventions the code follows.

## Contents

- [Python environment](#python-environment)
- [Linting and formatting](#linting-and-formatting)
- [Conventions](#conventions)
- [Where to change what](#where-to-change-what)

## Python environment

There are two [Poetry](https://python-poetry.org/) projects, both for **Python 3.10.14**:

| Project                                                    | Used for                                                                                |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| [`pipeline/pyproject.toml`](../pipeline/pyproject.toml)    | All scripts on your machine: pipeline, UMAP, BERTopic, loaders, fixtures, Alembic       |
| [`api/pyproject.toml`](../api/pyproject.toml)              | The API container ([`deploy/api.Dockerfile`](../deploy/api.Dockerfile)); also has the Python linters as dev dependencies |

### Set up the scripts environment

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

`python3.10` must be Python 3.10.14. If you do not have it, [uv](https://docs.astral.sh/uv/) can install it:

```bash
uv python install 3.10.14
```

Then pass the path from `uv python find 3.10.14` to `poetry -C pipeline env use`.

> [!NOTE]
> BERTopic depends on `hdbscan`, which is compiled during the installation. It needs a C compiler: the Xcode Command
> Line Tools on macOS, or `build-essential` on Debian and Ubuntu.

### Add or update packages

```bash
poetry -C pipeline add <package>
```

After editing a `pyproject.toml` by hand, update the lock file without upgrading other packages:

```bash
poetry -C pipeline lock --no-update
```

Rebuild the API image after changing `api/pyproject.toml`:

```bash
docker compose up -d --build api
```

## Linting and formatting

### Python

The code is formatted with [Black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/) and
checked with [Flake8](https://flake8.pycqa.org/). They are dev dependencies of `api/pyproject.toml`; without that
environment, run them with [uvx](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx black <path>
```

```bash
uvx isort --profile black <path>
```

```bash
uvx flake8 --max-line-length 120 <path>
```

The code base has not been formatted as a whole, so format only the files you change; otherwise the diff hides your
change.

### Frontend

In `frontend/`, with [ESLint](https://eslint.org/) (the Nuxt config) and [Prettier](https://prettier.io/):

```bash
npm run lint
```

```bash
npm run lint:fix
```

```bash
npm run format
```

`npm run lint` currently reports about 380 problems: mostly template style (self-closing tags, attribute order),
unused variables and `any` types. `npm run lint:fix` fixes about 260 of them (see [TODO](../TODO.md)).

### Editor

[`.editorconfig`](../.editorconfig) sets line endings, the final newline and the indentation for editors that support
it. In VS Code, format on save with these settings in `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }
}
```

## Conventions

### Naming

| What                          | Convention                         | Example                                           |
|-------------------------------|------------------------------------|---------------------------------------------------|
| Python files and folders      | `snake_case`                       | `load_mariadb_users.py`, `request_models/`        |
| Python classes                | `PascalCase`                       | `SDGLabelDecision`, `DecisionServiceSettings`     |
| Python functions, variables   | `snake_case`, constants `UPPER_SNAKE_CASE` | `verify_token()`, `MIN_PUBLICATIONS_PER_MAP` |
| Pydantic schemas              | `<Resource>Schema<Base\|Full>`     | `SDGGoalSchemaFull`                               |
| Vue components                | `PascalCase.vue`                   | `NavigationBar.vue`, `plots/ScatterPlot.vue`      |
| Composables                   | `use<Resource>.ts`                 | `useSDGs.ts`; plot helpers in `camelCase.ts`      |
| Pinia stores                  | `camelCase.ts`, `use<Name>Store`   | `sdgLabelDecisions.ts` → `useLabelDecisionsStore` |
| Pages                         | lowercase folders, `[param].vue`   | `pages/exploration/sdgs/[sdg]/[level].vue`        |
| TypeScript variables          | `camelCase`                        | `selectedSDG`                                     |
| Shell scripts                 | `kebab-case.sh`                    | `restore-qdrant.sh`                               |
| API paths                     | `kebab-case`, plural resources     | `/label-decisions`, `/sdg-predictions`            |

The API returns `snake_case` JSON; the frontend composables convert it to `camelCase`
([`snakeToCamel`](../frontend/utils/snakeToCamel.ts)).

### Scripts

- Scripts in `utils/` and `pipeline/` do their work in `main()` behind `if __name__ == "__main__":`, so importing
  them has no side effects.
- They run from the repository root with `PYTHONPATH=.` and read data from fixed paths under `data/`.
- Randomness uses the seed `31011997` from `SeedSettings`, so repeated runs give the same result.

### Commits

Write commit messages in the imperative ("Add …", "Fix …"), with a short subject line and, where it helps, a body that
explains why.

## Where to change what

| I want to …                                   | Change                                                                                  |
|-----------------------------------------------|-----------------------------------------------------------------------------------------|
| Add an API endpoint                           | A route in [`api/app/routes/`](../api/app/routes), its schema in [`schemas/`](../schemas), then [regenerate the Postman collection](api/README.md#updating-the-collection) |
| Add a database column                         | The model in [`models/`](../models), then a [migration](migrations.md)                  |
| Tune the game (votes per scenario, rewards)   | [`settings/settings.py`](../settings/settings.py) and [`services/`](../services)        |
| Change a GPT prompt                           | The strategy in [`services/gpt/strategies/`](../services/gpt/strategies)                |
| Add a page                                    | A file in [`frontend/pages/`](../frontend/pages); links go in [`NavigationBar.vue`](../frontend/components/NavigationBar.vue) |
| Call a new endpoint from the frontend         | The composable in [`frontend/composables/`](../frontend/composables), then the store    |
