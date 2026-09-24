# SDG Tag Heroes

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Nuxt](https://img.shields.io/badge/Nuxt-3-00DC82?logo=nuxt&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-collection-FF6C37?logo=postman&logoColor=white)

**SDG Tag Heroes** is a gamified, collaborative labeling platform that maps scientific publications to the
[UN Sustainable Development Goals (SDGs)](https://sdgs.un.org/goals). It was built as part of a master's thesis at
the University of Zurich (UZH).

Machine-learning models predict which of the 17 SDGs a publication addresses. Players ("heroes") then review those
predictions, vote on the correct SDG, write annotations, and earn XP and coins for their contributions. Once enough
votes are collected, a publication is assigned a **scenario** that tells players what kind of help it needs:

| Scenario        | Situation                                          | Example vote split |
|-----------------|----------------------------------------------------|--------------------|
| **Confirm**     | A clear favourite exists and needs confirmation    | 6 / 4              |
| **Tiebreaker**  | Two SDGs are tied                                  | 5 / 5              |
| **Investigate** | Votes are spread across several SDGs               | 3 / 3 / 3 / 1      |
| **Explore**     | No agreement at all                                | 1 / 2 / 2 / 2 / 1… |

When a consensus is reached, a **label decision** is stored (by majority, technocratic consensus, or expert decision).

Other features:

- **SDG predictions** per publication (goal and target level), with entropy and standard deviation as uncertainty measures
- **Exploration maps**: UMAP projections of publication embeddings, clustered into topics per SDG and level
- **Similarity search** over publication embeddings (Qdrant)
- **GPT-assisted features**: SDG explanations, keywords, facts, summaries, and comment/annotation evaluation (OpenAI)
- **Gamification**: XP banks and coin wallets per SDG, ranks, a leaderboard, quests, and user profiles

> [!NOTE]
> The original dataset consists of publications from [ZORA](https://www.zora.uzh.ch/), the UZH open repository.
> Those publications belong to their authors and UZH, so **the data is not part of this repository**. See
> [Data](#data) for what the application needs.

---

## Contents

- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
- [Services and ports](#services-and-ports)
- [API](#api)
- [Data](#data)
- [Dummy dataset](#dummy-dataset)
- [Building the dataset](#building-the-dataset)
- [Development](#development)
- [Documentation](#documentation)
- [Known issues](#known-issues)
- [Author](#author)

---

## Tech stack

| Area               | Technologies |
|--------------------|--------------|
| **Frontend**       | ![Nuxt](https://img.shields.io/badge/Nuxt_3-00DC82?logo=nuxt&logoColor=white) ![Vue.js](https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotjs&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white) ![Nuxt UI](https://img.shields.io/badge/Nuxt_UI-00DC82?logo=nuxt&logoColor=white) ![daisyUI](https://img.shields.io/badge/daisyUI-5A0EF8?logo=daisyui&logoColor=white) ![Pinia](https://img.shields.io/badge/Pinia-FFD859?logo=pinia&logoColor=black) ![D3.js](https://img.shields.io/badge/D3.js-F9A03C?logo=d3dotjs&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white) |
| **Backend**        | ![Python](https://img.shields.io/badge/Python_3.10-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/Alembic-6BA81E) ![JWT](https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white) ![Poetry](https://img.shields.io/badge/Poetry-60A5FA?logo=poetry&logoColor=white) |
| **Databases**      | ![MariaDB](https://img.shields.io/badge/MariaDB-003545?logo=mariadb&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white) ![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?logo=qdrant&logoColor=white) |
| **ML and AI**      | ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white) ![Hugging Face](https://img.shields.io/badge/Sentence_Transformers-FFD21E?logo=huggingface&logoColor=black) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white) ![UMAP](https://img.shields.io/badge/UMAP-5A5A5A) ![BERTopic](https://img.shields.io/badge/BERTopic-5A5A5A) ![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4o-412991?logo=openai&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white) |
| **Data pipeline**  | ![Prefect](https://img.shields.io/badge/Prefect-070E10?logo=prefect&logoColor=white) ZORA (OAI-PMH) harvesting, Aurora SDG models |
| **Infrastructure** | ![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?logo=docker&logoColor=white) ![Portainer](https://img.shields.io/badge/Portainer-13BEF9?logo=portainer&logoColor=white) ![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white) |

## Architecture

```
                     ┌──────────────────────────────┐
                     │  Frontend (Nuxt 3, Vue 3)    │  localhost:3000
                     │  frontend/                   │
                     └──────────────┬───────────────┘
                                    │ REST + JWT
                     ┌──────────────▼───────────────┐
                     │  API (FastAPI)               │  localhost:1002
                     │  api/ + models/ schemas/     │──────► OpenAI API
                     │  services/ settings/ ...     │
                     └──┬─────────┬─────────┬───────┘
                        │         │         │
            ┌───────────▼──┐ ┌────▼─────┐ ┌─▼──────────┐
            │ MariaDB      │ │ MongoDB  │ │ Qdrant     │
            │ core data    │ │ SDG      │ │ publication│
            │ (SQLAlchemy) │ │ explan-  │ │ embeddings │
            │              │ │ ations   │ │            │
            └──────────────┘ └──────────┘ └────────────┘
                        ▲
                        │ fills
            ┌───────────┴──────────────────────────────┐
            │  Dataset scripts (Python, optional       │
            │  Prefect flow): ZORA collector →         │
            │  predictor → embeddings → UMAP → topics  │
            └──────────────────────────────────────────┘
```

- **MariaDB** holds the relational core: publications, authors, SDG goals/targets, predictions, users, votes,
  annotations, label decisions, XP and coin histories, clusters, and dimensionality reductions. The schema is defined
  as SQLAlchemy models in [`models/`](models) and migrated with Alembic.
- **MongoDB** stores the precomputed SDG explanations (per-token attributions shown in the UI).
- **Qdrant** stores the publication embeddings (`sentence-transformers/all-MiniLM-L6-v2`, 384 dimensions) in the
  collection `publications-mt`, used for similarity search and UMAP.

## Repository structure

| Path                                          | Content                                                                          |
|-----------------------------------------------|----------------------------------------------------------------------------------|
| [`api/`](api)                                 | FastAPI application ([`api/app/main.py`](api/app/main.py)) and its routes        |
| [`models/`](models)                           | SQLAlchemy ORM models (MariaDB tables)                                           |
| [`schemas/`](schemas)                         | Pydantic response schemas                                                        |
| [`request_models/`](request_models)           | Pydantic request bodies                                                          |
| [`services/`](services)                       | Business logic: decisions, rewards, scoring, labels, metrics, GPT strategies     |
| [`enums/`](enums)                             | Shared enums (roles, scenario types, vote types, …)                              |
| [`settings/`](settings)                       | Central configuration ([`settings.py`](settings/settings.py)) and SDG texts      |
| [`db/`](db)                                   | Database connectors and scripts to create/check the MariaDB schema               |
| [`alembic/`](alembic)                         | Database migrations                                                              |
| [`pipeline/`](pipeline)                       | Data pipeline: ZORA harvesting, SDG prediction, embedding, UMAP (Prefect flow)   |
| [`utils/`](utils)                             | Loader scripts for MariaDB/MongoDB/Qdrant, backup/restore scripts, logger        |
| [`frontend/`](frontend)                       | Nuxt 3 frontend (Nuxt UI 2, Tailwind 3, daisyUI 4, D3, Pinia)                    |
| [`deploy/`](deploy)                           | Dockerfiles and container entrypoints                                            |
| [`env/`](env)                                 | Environment files (only `*.example` templates are committed)                     |
| [`notebooks/`](notebooks)                     | Exploration notebooks (topic modelling, model comparison)                        |
| [`prompts/`](prompts)                         | Example prompt and answer for the GPT assistant                                  |
| [`docs/`](docs)                               | Developer notes (API and Postman, Docker, databases, migrations, deployment)     |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose v2
- [Node.js](https://nodejs.org/) 20 and npm (for the frontend)
- An [OpenAI API key](https://platform.openai.com/api-keys) for the GPT features (the rest works without it)
- To build the dataset (pipeline and loader scripts, Alembic): Python **3.10.14** and
  [Poetry](https://python-poetry.org/) (see [Running the scripts](#running-the-scripts))

## Getting started

These steps start the databases, the API, and the frontend on your machine.

### 1. Clone the repository

```bash
git clone https://github.com/HuberNicolas/sdg-tag-heroes.git
```

```bash
cd sdg-tag-heroes
```

### 2. Create the environment files

Every service reads its configuration from `env/<service>.env`. Copy all templates:

```bash
for f in env/*.env.example; do cp "$f" "${f%.example}"; done
```

Then open each file in `env/` and fill in the empty values:

| File                    | What to set                                                                                  |
|-------------------------|----------------------------------------------------------------------------------------------|
| `mariadb.env`           | `MYSQL_ROOT_PASSWORD`, `MARIADB_USER`, `MARIADB_PASSWORD` (database name defaults to `igcl`) |
| `mongodb.env`           | `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, `MONGODB_HOST=mongodb`           |
| `mongo-express.env`     | UI login and `ME_CONFIG_MONGODB_URL=mongodb://<user>:<password>@mongodb:27017`               |
| `backend.env`           | `SECRET_KEY` (a long random string used to sign JWTs)                                        |
| `api.env`               | `OPENAI_API_KEY`                                                                             |
| `users.env`             | The initial accounts (admin, labeler, expert). **Change the default passwords.**             |

### 3. Provide the data folder

The API image copies `data/api/` at build time (the trained UMAP models), and several loader scripts read from
`data/`. The folder is git-ignored and not published. See [Data](#data) for the expected layout.

### 4. Start the databases and the API

```bash
docker compose up -d --build api mariadb phpmyadmin mongodb mongo-express qdrantdb
```

`docker compose --profile prod up -d --build` starts the same services plus the frontend and Portainer.

Check that the API is up and connected to all databases:

```bash
docker compose logs -f api
```

The API is now available at <http://localhost:1002>, with interactive docs at <http://localhost:1002/docs>.

### 5. Fill the databases

**Option A: restore a backup** (recommended if you have one). With the containers running:

```bash
docker exec -i mariadb-database sh -c 'mariadb -u root -p"$MYSQL_ROOT_PASSWORD" igcl' < data/db/igcl_dump.sql
```

```bash
curl -X POST 'http://localhost:2003/collections/publications-mt/snapshots/upload' -F 'snapshot=@data/db/<snapshot-file>.snapshot'
```

For MongoDB, follow the `mongorestore` steps in [`docs/data-related/db.md`](docs/data-related/db.md).

**Option B: build the dataset from scratch.** This takes several steps (harvesting, ML predictions, embeddings, topic
models, simulated players). They are described in order in [Building the dataset](#building-the-dataset).

**Option C: load the dummy dataset.** Without access to the original data, generate fictional publications and run
the pipeline on them; see [Dummy dataset](#dummy-dataset).

### 6. Start the frontend

The frontend reads the API address from `frontend/.env`:

```bash
cp frontend/.env.example frontend/.env
```

Set `API_URL=http://localhost:1002` in `frontend/.env`. Then start the frontend either in Docker or on your machine.

**In Docker** (hot reload included):

```bash
docker compose up -d --build frontend
```

Open <http://localhost:3030>. After changing `frontend/package.json`, rebuild with
`docker compose up -d --build --force-recreate -V frontend`, so the container gets fresh `node_modules`.

**On your machine** (Node.js 20 or newer):

```bash
cd frontend
```

```bash
npm install
```

```bash
npm run dev
```

Open <http://localhost:3000>.

Log in with one of the accounts from `env/users.env`.

**Production build**: [`deploy/frontend.prod.Dockerfile`](deploy/frontend.prod.Dockerfile) builds the frontend and serves
it with the Nuxt server on port 3000. Pass the API address at runtime:

```bash
docker build -f deploy/frontend.prod.Dockerfile -t sdg-tag-heroes-frontend-prod .
```

```bash
docker run -p 3000:3000 -e NUXT_PUBLIC_API_URL=http://localhost:1002 sdg-tag-heroes-frontend-prod
```

### Stop everything

```bash
docker compose down
```

Database contents are stored in `data/docker/` and survive a restart.

## Services and ports

All services run in the Docker network `sdg-tag-heroes-net` (`10.5.0.0/24`).

| Service         | Container          | Host port | Profile    | Purpose                                     |
|-----------------|--------------------|-----------|------------|---------------------------------------------|
| `api`           | `api`              | 1002      | prod       | FastAPI backend (hot reload on code change) |
| `mariadb`       | `mariadb-database` | 2001      | prod       | Relational database                         |
| `phpmyadmin`    | `phpmyadmin`       | 2011      | prod       | MariaDB web UI                              |
| `mongodb`       | `mongodb-database` | 2002      | prod       | Document database (SDG explanations)        |
| `mongo-express` | `mongo-express`    | 2022      | prod       | MongoDB web UI                              |
| `qdrantdb`      | `qdrant-database`  | 2003      | prod       | Vector database; dashboard at `/dashboard`  |
| `frontend`      | `frontend`         | 3030      | prod       | Nuxt dev server with hot reload             |
| `portainer`     | `portainer`        | 1000      | prod       | Docker management UI                        |
| `utils`         | `utils`            | –         | dev, debug | Shell with MariaDB and MongoDB client tools |

The dataset scripts (pipeline, loaders) do not run in a container; see [Running the scripts](#running-the-scripts).

How to log in to each database UI is described in [`docs/data-related/db.md`](docs/data-related/db.md).

## API

The API is a FastAPI application. With the containers running, the interactive reference is at
<http://localhost:1002/docs> (Swagger UI) and <http://localhost:1002/redoc>.

A **Postman collection** with all endpoints is in
[`docs/api/sdg-tag-heroes.postman_collection.json`](docs/api/sdg-tag-heroes.postman_collection.json). Import it, set the
`password` variable, and send **auth → Login**; the token is then used by every other request. Details, variables, and
how to regenerate the collection are in [`docs/api/README.md`](docs/api/README.md).

### Authentication

Get a JWT by posting email and password as JSON:

```bash
curl -X POST http://localhost:1002/auth/login -H 'Content-Type: application/json' -d '{"email": "labeler@tagheroes.ch", "password": "<password>"}'
```

Send the returned token as `Authorization: Bearer <token>` with every other request. In Swagger UI, use the
**Authorize** button. Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (set in `env/backend.env`).

### Endpoints

| Prefix                       | Resource                                                              |
|------------------------------|-----------------------------------------------------------------------|
| `/auth`                      | Login and token check                                                 |
| `/users`                     | Users, own profile, filtering by role                                 |
| `/users-profiles`            | GPT suggestions: which SDG fits a user's skills or interests          |
| `/publications`              | Publications, filtering, similarity search, GPT summaries/keywords/facts |
| `/authors`                   | Authors                                                               |
| `/sdgs`                      | SDG goals and targets                                                 |
| `/sdg-predictions`           | Model predictions per publication                                     |
| `/explanations`              | Token-level SDG explanations (MongoDB)                                |
| `/dimensionality-reductions` | UMAP coordinates for the exploration maps                             |
| `/collections`               | Topic collections                                                     |
| `/user-labels`               | Votes and comments players give on a publication                      |
| `/votes`                     | Up/down votes on user labels                                          |
| `/annotations`               | Annotations on publications                                           |
| `/label-summaries`           | Aggregated labels per publication                                     |
| `/label-histories`           | History of label changes                                              |
| `/label-decisions`           | Scenarios and final label decisions                                   |
| `/banks`                     | XP per SDG and its history                                            |
| `/wallets`                   | Coins per SDG and its history                                         |
| `/ranks`                     | SDG ranks of users                                                    |

## Data

The application expects a `data/` folder in the repository root. It is not published because it contains UZH
publications and derived artefacts.

The ground-truth labels, the SDG clusters, and the SDG explanations come from **SDG-Scout**, an earlier project of the
same research group at UZH, and were created together with that group. They are not publicly available either. To
run the application without the original data, use the [dummy dataset](#dummy-dataset).

The relevant parts:

```
data/
├── api/umap_model/                  # Trained UMAP models, copied into the API image (step 7)
├── db/
│   ├── igcl_dump.sql                # MariaDB dump (restore)
│   ├── *.snapshot                   # Qdrant snapshot of publications-mt (restore)
│   ├── explanations/                # Split SDG explanations for MongoDB (step 10)
│   ├── sdg_label_summary.txt        # Ground-truth labels (step 9)
│   ├── full_dataset_clusters.json   # SDG clusters (step 8)
│   └── publications_clusters.txt    # Publication-to-cluster assignment (step 8)
├── docker/                          # Volumes of the running containers (created automatically)
├── icons/                           # SDG goal/target SVGs and sdg_extras.json (step 2)
├── pipeline/
│   ├── aurora_models/               # Downloaded Aurora models (step 5)
│   ├── model/                       # SciBERT model (alternative predictor)
│   └── collections/                 # BERTopic output: uzh_topic_data.csv, uzh_topic_info_simplified.csv (step 8)
└── ranks/sdg_ranks.json             # Rank definitions (step 2)
```

To delete all container data and start from empty databases, run `bash utils/docker/delete-docker-data.sh` (it removes
`data/docker/`).

## Dummy dataset

The companion repository [sdg-tag-heroes-dataset-generator](https://github.com/HuberNicolas/sdg-tag-heroes-dataset-generator)
generates fictional publications, so the application can be built and run without the original data. It only
replaces the two external sources; everything else is computed by this repository's pipeline:

| Original source | Replaced by the generator                                                     | Used by                                   |
|-----------------|--------------------------------------------------------------------------------|-------------------------------------------|
| ZORA            | Publications as OAI-PMH files in `data/pipeline/oai/`                          | `collector.py --from-dir`                 |
| SDG-Scout       | Ground-truth labels (`data/db/sdg_label_summary.txt`), explanations (`data/db/explanations/`) | label and explanation loaders |
| —               | Placeholder SDG icons, SDG texts, rank tiers (`data/icons/`, `data/ranks/`)    | SDG and rank loaders                      |

The SDG predictions come from the SciBERT model `Dvdblk` (the Aurora models need TensorFlow, see
[SDG predictions](#5-sdg-predictions)), so the application runs with `PREDICTION_MODEL=Dvdblk`.

> [!WARNING]
> Load the dummy dataset only into empty databases. [`utils/dummy/load_dummy_dataset.py`](utils/dummy/load_dummy_dataset.py)
> refuses to run otherwise, and a resumed run only continues when every publication in MariaDB comes from the dummy
> dataset.

1. Generate the data (see the generator's README; `--mode llm` writes more realistic abstracts with Claude) and copy
   its `output/data/` into `data/`.
2. Start the databases and the API:

   ```bash
   PREDICTION_MODEL=Dvdblk docker compose up -d --build api mariadb mongodb qdrantdb
   ```

3. Set up the Python environment for the dataset scripts, as described in [Running the scripts](#running-the-scripts).
4. Run all steps with one command, from the repository root. It runs the regular scripts one after the other: schema,
   collector (from the files), SciBERT predictions, embeddings, UMAP maps, BERTopic topics, then SDGs, users, labels,
   topics, explanations, and simulated players. For 600 publications it took 8 minutes on a laptop CPU.

   ```bash
   PYTHONPATH=. python utils/dummy/load_dummy_dataset.py
   ```

5. Restart the API so it loads the new UMAP models, and start the frontend with a small number of map parts (the
   overview map is split into parts, one per universe):

   ```bash
   docker compose restart api
   ```

   Set `NUXT_PUBLIC_MAP_PARTITIONS=3` in `frontend/.env`, then start the frontend as in
   [Getting started](#6-start-the-frontend).

A step that fails can be resumed with `--from-step <name>`; the script prints the command. Log in with an account from
`env/users.env`, or with one of the 40 generated players (`<lastname>@example.org`, password `password01`).

**Limitations:** the template abstracts (the generator's default mode) share many phrases, so BERTopic finds only a
few topics; abstracts written with `--mode llm` give more varied topics. SciBERT rarely predicts SDG 17 above 0.7, so
that SDG may have no map.

## Building the dataset

This section explains how the databases are filled from nothing: which script creates which data, what it needs as
input, and in which order to run the scripts. If you have a backup, [restoring it](#5-fill-the-databases) is much
faster.

> [!WARNING]
> Many loader scripts run as soon as they are executed and some **drop the database or collection** they fill first
> (for example all scripts in `utils/mongodb/`). Run them only against a database you can rebuild.

### Overview

```
 1. Schema                 init_mariadb.py, alembic
 2. Reference data         SDG goals & targets, icons, texts, ranks
 3. Users                  real accounts from users.env or generated players
 4. Publications           pipeline: ZORA collector
 5. Predictions            pipeline: Aurora goal/target models → entropy & std
 6. Embeddings             pipeline: loader → Qdrant
 7. Maps                   UMAP projections per SDG and level
 8. Topics & clusters      BERTopic collections, SDG clusters
 9. Ground-truth labels    label summaries + histories
10. Explanations           token-level SDG explanations → MongoDB
11. Fixtures               simulated game activity (personas, votes, scenarios, XP, coins)
```

Each step depends on the ones before it. For example, the fixtures need users, experts, publications, and ground-truth
labels.

### Running the scripts

The scripts are standalone Python files that run on your machine, not in a container. Run them **from the repository
root** with `PYTHONPATH=.`, while the database containers are running. They connect through the `*_LOCAL` host and
port values in `env/*.env`.

All of them use the Poetry environment in [`pipeline/pyproject.toml`](pipeline/pyproject.toml) (Python 3.10.14:
pipeline, UMAP, BERTopic, loaders, fixtures, Alembic). [`api/pyproject.toml`](api/pyproject.toml) is the environment
of the API container. Create and activate the environment once:

```bash
poetry -C pipeline env use python3.10
```

```bash
poetry -C pipeline install --no-root
```

```bash
source "$(poetry -C pipeline env info --path)/bin/activate"
```

`python3.10` must be Python 3.10.14; if you do not have it, [uv](https://docs.astral.sh/uv/) can install it
(`uv python install 3.10.14`, then pass the path from `uv python find 3.10.14` to `env use`). Compiling `hdbscan`
(for BERTopic) needs a C compiler (Xcode Command Line Tools on macOS, `build-essential` on Debian and Ubuntu).

Most loaders read hard-coded paths under `data/` and use the seed `31011997` (from
[`settings/settings.py`](settings/settings.py)), so repeated runs produce the same data.

### 1. Schema

Create all tables from the SQLAlchemy models, then tell Alembic that the database is on the latest migration:

```bash
PYTHONPATH=. python db/scripts/init_mariadb.py
```

```bash
alembic stamp head
```

For later schema changes, see [`docs/data-related/migrations.md`](docs/data-related/migrations.md). To start over,
[`utils/mariadb/drop_mariadb_tables.py`](utils/mariadb/drop_mariadb_tables.py) drops every table, and
[`db/scripts/check_mariadb.py`](db/scripts/check_mariadb.py) lists the tables with their row counts.

### 2. Reference data

| Script                                                                       | Reads                               | Writes                                                  |
|------------------------------------------------------------------------------|-------------------------------------|---------------------------------------------------------|
| [`load_mariadb_sdg.py`](utils/mariadb/load_mariadb_sdg.py)                   | `data/icons/` (goal and target SVGs) | 17 SDG goals and 169 targets with colours and icons     |
| [`load_mariadb_sdg_extras.py`](utils/mariadb/load_mariadb_sdg_extras.py)     | `data/icons/sdg_extras.json`        | Short titles, keywords, and explanations for each goal  |
| [`load_mariadb_sdg_ranks.py`](utils/mariadb/load_mariadb_sdg_ranks.py)       | `data/ranks/sdg_ranks.json`         | 4 rank tiers per SDG with name and XP threshold         |
| [`load_mongodb_sdg.py`](utils/mongodb/load_mongodb_sdg.py)                   | `data/icons/`                       | The same SDG goals and targets in MongoDB               |

The first three are in `utils/mariadb/`, the last in `utils/mongodb/`. Run them in this order.

### 3. Users

[`utils/mariadb/load_mariadb_users.py`](utils/mariadb/load_mariadb_users.py) creates users with their inventory and
their role entries (labeler, expert, admin):

```bash
PYTHONPATH=. python utils/mariadb/load_mariadb_users.py
```

creates the accounts defined in `env/users.env` (`USER_COUNT`, then `USER_<i>_EMAIL`, `USER_<i>_PASSWORD`,
`USER_<i>_ROLE` and optionally `USER_<i>_NICKNAME` for each user, numbered from 0 or 1).

```bash
PYTHONPATH=. python utils/mariadb/load_mariadb_users.py --generate 40
```

creates 40 generated labelers with Faker, e-mail addresses like `<lastname>@example.org`, and the password
`password01`. Labeler and expert scores are random.

The fixtures (step 11) need at least one user with the `expert` role, so put an expert in `users.env`.

### 4. Publications

The collector in [`pipeline/zora/collector.py`](pipeline/zora/collector.py) harvests publications from the
[ZORA OAI-PMH endpoint](https://www.zora.uzh.ch/cgi/oai2) and stores them with authors, faculties, institutes, and
divisions. Settings (limit, paths) are in `CollectorSettings`.

```bash
PYTHONPATH=. python pipeline/zora/collector.py --db mariadb --reset false --recreate_organizational_structure true
```

With `--from-dir <folder>`, the collector reads the OAI-PMH responses from files instead of ZORA (`ListSets.xml`,
`ListRecords.xml` and one file per `resumptionToken`). The [dummy dataset](#dummy-dataset) uses this.

### 5. SDG predictions

[`pipeline/zora/aurora_model_loader.py`](pipeline/zora/aurora_model_loader.py) downloads the pretrained
[Aurora](https://aurora-universities.eu/) SDG models from Zenodo (links in
[`aurora-model-goal-only-links.csv`](pipeline/zora/aurora-model-goal-only-links.csv)) into `data/pipeline/aurora_models/`.
Then:

| Script                                                                            | Result                                                                  |
|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| [`pipeline/zora/predictor.py`](pipeline/zora/predictor.py)                        | One score per SDG goal and publication (`prediction_model = "Aurora"`) |
| [`pipeline/zora/target_predictor.py`](pipeline/zora/target_predictor.py)          | Scores for the SDG targets                                              |
| [`utils/mariadb/load_mariadb_sdg_predictions_entropy.py`](utils/mariadb/load_mariadb_sdg_predictions_entropy.py) | Entropy and standard deviation of each prediction (used as uncertainty) |
| [`utils/mariadb/load_mariadb_scaler.py`](utils/mariadb/load_mariadb_scaler.py)    | Optional experiment: rescaled copies (`Scaled_Aurora`), limited to 5    |

Both predictors take `--db mariadb --batch_size <n> --mariadb_batch_size <n>`. The threshold for "this publication
belongs to an SDG" is `DEFAULT_PREDICTION_THRESHOLD` (0.98) in `MariaDBSettings`.

Maps, levels, and quests use the predictions of one model, `DEFAULT_PREDICTION_MODEL` in `MariaDBSettings`. It is
set with the environment variable `PREDICTION_MODEL`: `Aurora` (default, the thesis dataset) or `Dvdblk` (the dummy
dataset). `docker-compose.yml` passes it to the `api` container; for the scripts, set it in your shell.

> [!NOTE]
> The Aurora models are Keras models and need **TensorFlow 2.11**, which is not part of
> [`pipeline/pyproject.toml`](pipeline/pyproject.toml) (it is commented out there). Run `predictor.py` and
> `target_predictor.py` in an environment with TensorFlow 2.11 installed.

**Alternative model:** [`pipeline/zora/predictor_dvdblk.py`](pipeline/zora/predictor_dvdblk.py) predicts the goals with
the SciBERT model [`dvdblk/scibert_sdg_cased_zo-up`](https://huggingface.co/dvdblk/scibert_sdg_cased_zo-up) (PyTorch, no
TensorFlow needed) and stores them with `prediction_model = "Dvdblk"`. The model is downloaded on first use to
`data/pipeline/model/scibert_sdg_classification` ([`utils/sdg_predictor.py`](utils/sdg_predictor.py)). The SDG
explanations from SDG-Scout were computed with this model.

```bash
PYTHONPATH=. python pipeline/zora/predictor_dvdblk.py --db mariadb
```

Other experiments are kept for reference: [`pipeline/zora/predictor_bielik.py`](pipeline/zora/predictor_bielik.py) and
fine-tuning of the Aurora models in [`pipeline/aurora/fine_tune.py`](pipeline/aurora/fine_tune.py).

### 6. Embeddings

[`pipeline/zora/loader.py`](pipeline/zora/loader.py) embeds `"Title: … Abstract: …"` of every publication with
`sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) and stores the vectors in the Qdrant collection
`publications-mt`, with the MariaDB ID in the payload field `sql_id`.

```bash
PYTHONPATH=. python pipeline/zora/loader.py --db mariadb --batch_size 64
```

### 7. Maps (UMAP)

The exploration maps show publications as points in 2D. The coordinates are stored as dimensionality reductions:

| Script                                                                          | What it projects                                                                                                             |
|---------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| [`load_mariadb_umap.py`](utils/mariadb/load_mariadb_umap.py)                    | Per SDG, 3 **levels** by prediction score: 1.0–0.98, 0.98–0.9, 0.9–0.7 (`FILTER_RANGES`). Saves one model per SDG to `data/api/umap_model/config_15_0.0_2/`. |
| [`load_mariadb_umap_complete.py`](utils/mariadb/load_mariadb_umap_complete.py)  | All publications, split into 9 partitions of 13,000 (`MAP_PARTITION_SIZE`), stored as `SDG0-level<n>`                        |
| [`pipeline/zora/reducer.py`](pipeline/zora/reducer.py)                          | The pipeline version of the same step                                                                                        |

UMAP parameters (`n_neighbors=15`, `min_dist=0.0`, `n_components=2`) are in `ReducerSettings`. The API loads the saved
models from `data/api/umap_model/` to place new points on the map.

### 8. Topics and clusters

**Collections** are the topics shown on the overview map:

1. [`utils/mariadb/generate_umap_with_tm.py`](utils/mariadb/generate_umap_with_tm.py) fits a
   [BERTopic](https://maartengr.github.io/BERTopic/) model on all embeddings from Qdrant (HDBSCAN, c-TF-IDF, SDG
   descriptions as seed words), reduces it to 20 topics plus one outlier topic, and writes `uzh_topic_data.csv` and
   `uzh_topic_info.csv` to `data/pipeline/collections/`. ([`generate_topic_model.py`](utils/mariadb/generate_topic_model.py)
   is an earlier version; [`notebooks/topic_model.ipynb`](notebooks/topic_model.ipynb) is the exploration.)
2. [`utils/mariadb/simplify_topic_info.py`](utils/mariadb/simplify_topic_info.py) adds a short readable name per
   topic (`GPT_Name`) and writes `uzh_topic_info_simplified.csv`. For the thesis dataset, these names were written
   by hand with ChatGPT; the script builds them from the two top keywords.
3. [`utils/mariadb/load_mariadb_collections.py`](utils/mariadb/load_mariadb_collections.py) loads the topics as
   collections and the 2D positions as reductions with the shorthand `TM-UZH-UMAP-15-0.0-2`.

**Clusters** (per SDG, 25 levels with 1 to 25 topics each) are loaded from prepared files:

- [`load_mariadb_clusters.py`](utils/mariadb/load_mariadb_clusters.py) reads `data/db/full_dataset_clusters.json`
  (centres, sizes, labels) into cluster groups, levels, and topics
- [`load_mariadb_clusters_publications.py`](utils/mariadb/load_mariadb_clusters_publications.py) reads
  `data/db/publications_clusters.txt` and assigns publications to clusters
- [`load_mongodb_clusters.py`](utils/mongodb/load_mongodb_clusters.py) writes the same clusters to MongoDB

The cluster files come from SDG-Scout (see [Data](#data)). The clusters were not used in the deployed version.

### 9. Ground-truth labels

[`utils/mariadb/load_mariadb_sdg_label_summaries.py`](utils/mariadb/load_mariadb_sdg_label_summaries.py) reads
`data/db/sdg_label_summary.txt`: SQL-style tuples `(publication_id, sdg1, …, sdg17)` with `1` for the correct SDG. For
each tuple it creates a label summary and a label history. These labels are the "truth" that the fixtures use to
simulate votes. The labels come from SDG-Scout (see [Data](#data)).

### 10. Explanations

The explanations show which words of an abstract point to an SDG. They were precomputed in SDG-Scout (see
[Data](#data)) and are stored in MongoDB, database `sdg_explanations`:

1. Split the export into files of 10,000 lines with
   [`utils/mongodb/sdg-explanation-splitter.sh`](utils/mongodb/sdg-explanation-splitter.sh) (run it next to
   `sdg_explanations.json`) and put the parts in `data/db/explanations/`.
2. [`load_mongodb_explanations.py`](utils/mongodb/load_mongodb_explanations.py) loads them into the collection
   `explanations`.
3. [`load_mongodb_small_explanations.py`](utils/mongodb/load_mongodb_small_explanations.py) stores the token scores as
   integers (× 10,000) to reduce the size (about 30 % smaller). It writes to the collection the API reads,
   `explanations_scaled_new` (`MongoDBSDGSettings.DB_COLLECTION_NAME`), and replaces it on every run.

[`debug_mongo.py`](utils/mongodb/debug_mongo.py) removes duplicate explanations.

### 11. Fixtures: simulated game activity

[`utils/mariadb/load_mariadb_fixtures.py`](utils/mariadb/load_mariadb_fixtures.py) fills the game tables so the
application looks like it has been played. It needs users (with at least one expert), publications, label summaries,
and label histories.

> [!WARNING]
> The fixtures call the OpenAI API for every generated comment and annotation, so a run costs money and takes a while.
> An `OPENAI_API_KEY` in `env/api.env` is required. The script also **truncates** the tables for user labels, votes,
> annotations, label decisions, wallets, and XP banks before it starts.

What it does, in order:

1. **Personas**: each user gets a temporary [Bartle player type](https://en.wikipedia.org/wiki/Bartle_taxonomy_of_player_types)
   (Achiever, Explorer, Socializer, Killer), a trust score, an interest, and a skill
   ([`utils/personas/personas_generator.py`](utils/personas/personas_generator.py)). Personas are not stored in the
   database.
2. **Wallets and XP banks** for every user, with 5 history entries each.
3. **Scenario decisions**: for up to 500 publications that have a ground-truth label, it picks a scenario and creates
   `VOTES_NEEDED_FOR_SCENARIO` (10) user labels whose distribution matches it. The true SDG always wins or is part of
   the tie:

   | Scenario    | Distribution                          |
   |-------------|---------------------------------------|
   | Confirm     | 90 % true SDG, 10 % another SDG       |
   | Tiebreaker  | 50 % true SDG, 50 % another SDG       |
   | Investigate | 3 / 3 / 3 / 1                          |
   | Explore     | 1 / 2 / 2 / 2 / 1 / 1 / 1              |

4. **Comments and annotations**: GPT writes them in the voice of the user's persona
   ([`persona_comment_generator_strategy.py`](services/gpt/strategies/persona_comment_generator_strategy.py)).

The ratios are in `FixturesSettings` and the vote thresholds in `DecisionServiceSettings`. The number of users and
publications are parameters of `populate_db()`. It also contains older random generators (user labels, votes,
annotations, decisions) that are disabled with `if False:`.

### GPT evaluation datasets (optional)

These scripts are not needed to run the application. They create datasets for the thesis evaluation: how well GPT
agrees with the model predictions. They read publications that have a ground-truth label and write CSV files into the
current directory.

| Script                                                                                                   | Output                                   | What it asks GPT                                                                                           |
|----------------------------------------------------------------------------------------------------------|------------------------------------------|------------------------------------------------------------------------------------------------------------|
| [`generate_confidence_score.py`](utils/dataset/generate_confidence_score.py)                             | `chatgpt_sdg_classification_results.csv` | An initial SDG guess with reasoning and confidence, then an assessment of the model's prediction            |
| [`chatgpt_dataset_generation.py`](utils/dataset/chatgpt_dataset_generation.py)                           | `sdg_evaluation_results_with_costs.csv`  | Relevance and confidence for all 17 SDGs, arguments for and against one SDG, plus estimated API cost        |
| [`chatgpt_dataset_generation_batchify.py`](utils/dataset/chatgpt_dataset_generation_batchify.py)         | `batch_results.csv`                      | The same through the cheaper OpenAI Batch API                                                              |

The number of publications per SDG is set by `LIMIT` (or `.limit()`) in each script.

### Pipeline with Prefect

Steps 4 to 7 can also run as one [Prefect](https://www.prefect.io/) flow
([`pipeline/prefect/flow.py`](pipeline/prefect/flow.py)): collector → predictor (Aurora) → loader → reducer. Batch
sizes are in `PrefectSettings`. Run it in the same environment as the other scripts:

```bash
PYTHONPATH=. python pipeline/prefect/flow.py
```

Without a Prefect server, Prefect runs the flow in a temporary local instance. To follow it in the Prefect UI, start
`prefect server start` in a second terminal first.

## Development

- **Database migrations**: change a model in `models/`, then run `alembic revision --autogenerate -m "…"` and
  `alembic upgrade head`. Details in [`docs/data-related/migrations.md`](docs/data-related/migrations.md).
- **Models vs. schemas**: see [`docs/data-related/orm.md`](docs/data-related/orm.md).
- **Linting and formatting**: Black, isort, and Flake8 for Python; ESLint and Prettier for the frontend
  (`npm run lint`, `npm run format`). See [`docs/development/linting.md`](docs/development/linting.md).
- **Configuration**: tunable values (prediction model and threshold, votes needed for a scenario, GPT model, UMAP
  parameters, …) are in [`settings/settings.py`](settings/settings.py).
- **Logs** of the API are written to `data/docker/logs/`.

## Documentation

More detailed notes are in [`docs/`](docs):

| Topic                            | File                                                                   |
|----------------------------------|------------------------------------------------------------------------|
| API reference and Postman        | [`docs/api/README.md`](docs/api/README.md)                             |
| Database UIs, backup and restore | [`docs/data-related/db.md`](docs/data-related/db.md)                   |
| Alembic migrations               | [`docs/data-related/migrations.md`](docs/data-related/migrations.md)   |
| Models vs. schemas               | [`docs/data-related/orm.md`](docs/data-related/orm.md)                 |
| Schemas and TypeScript types     | [`docs/data-related/schemas.md`](docs/data-related/schemas.md)         |
| Query layer                      | [`docs/data-related/queries.md`](docs/data-related/queries.md)         |
| Python environments (Poetry)     | [`docs/python-env.md`](docs/python-env.md)                             |
| Docker commands                  | [`docs/docker.md`](docs/docker.md)                                     |
| Deployment on the UZH server     | [`docs/deployment/deployment.md`](docs/deployment/deployment.md)       |
| Linting and code style           | [`docs/development/`](docs/development)                                |
| Solved problems                  | [`docs/issues.md`](docs/issues.md)                                     |

## Known issues

- An attempt to upgrade the frontend to Nuxt UI 3, Tailwind 4, and daisyUI 5 was not finished. It is kept on the
  branch `archive/frontend-nuxt-ui-3`.
- The Aurora predictors need TensorFlow 2.11, which is not in the pipeline's Poetry environment (see
  [SDG predictions](#5-sdg-predictions)).

## Author

Nicolas Huber, master's thesis, University of Zurich (UZH).
