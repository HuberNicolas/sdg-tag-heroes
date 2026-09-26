# Building the dataset

This guide explains how the databases are filled from nothing: which script creates which data, what it reads, and
in which order the scripts run. The [README](../README.md#building-the-dataset) has the short version.

> [!TIP]
> - **No original data?** Use the [dummy dataset](../README.md#dummy-dataset). One command runs all of the steps
>   below on generated publications.
> - **Have a backup?** [Restoring it](databases.md#backup-and-restore) is much faster than rebuilding.

> [!WARNING]
> Some scripts **drop the database or collection** they fill before they load it (for example every script in
> `utils/mongodb/`). The fixtures truncate the game tables. Run the scripts only against databases you can rebuild.

## Contents

- [Overview](#overview)
- [Running the scripts](#running-the-scripts)
- [1. Schema](#1-schema)
- [2. Reference data](#2-reference-data)
- [3. Users](#3-users)
- [4. Publications](#4-publications)
- [5. SDG predictions](#5-sdg-predictions)
- [6. Embeddings](#6-embeddings)
- [7. Maps (UMAP)](#7-maps-umap)
- [8. Topics and clusters](#8-topics-and-clusters)
- [9. Ground-truth labels](#9-ground-truth-labels)
- [10. Explanations](#10-explanations)
- [11. Fixtures: simulated game activity](#11-fixtures-simulated-game-activity)
- [GPT evaluation datasets (optional)](#gpt-evaluation-datasets-optional)

## Overview

| Step | What                     | Main scripts                                              | Writes to        |
|-----:|--------------------------|-----------------------------------------------------------|------------------|
|    1 | Schema                   | `db/scripts/init_mariadb.py`, `alembic stamp head`        | MariaDB          |
|    2 | Reference data           | SDG goals and targets, icons, texts, ranks                | MariaDB, MongoDB |
|    3 | Users                    | accounts from `env/users.env`, generated players          | MariaDB          |
|    4 | Publications             | ZORA collector                                            | MariaDB          |
|    5 | Predictions              | Aurora or SciBERT (`Dvdblk`), then entropy                | MariaDB          |
|    6 | Embeddings               | `pipeline/zora/loader.py`                                 | Qdrant           |
|    7 | Maps                     | UMAP projections per SDG and level                        | MariaDB, `data/api/` |
|    8 | Topics and clusters      | BERTopic collections, SDG clusters                        | MariaDB, MongoDB |
|    9 | Ground-truth labels      | label summaries and histories                             | MariaDB          |
|   10 | Explanations             | token-level SDG explanations                              | MongoDB          |
|   11 | Fixtures                 | simulated players' votes, comments, scenarios, XP, coins  | MariaDB          |

Each step depends on the ones before it. For example, the fixtures need users, experts, publications and ground-truth
labels. [`utils/dummy/load_dummy_dataset.py`](../utils/dummy/load_dummy_dataset.py) lists the exact order in which it
runs the scripts.

## Running the scripts

The scripts are standalone Python files that run on your machine, not in a container. Start the database containers
first, then run every script **from the repository root** with `PYTHONPATH=.`. Outside Docker, the scripts connect
through the `*_LOCAL` host and port values in `env/*.env`.

All scripts share the Poetry environment in [`pipeline/pyproject.toml`](../pipeline/pyproject.toml) (Python
3.10.14). [Development](development.md#python-environment) explains how to set it up.

Most loaders read fixed paths under `data/` and use the seed `31011997` from
[`settings/settings.py`](../settings/settings.py), so repeated runs produce the same data.

## 1. Schema

Create all tables from the SQLAlchemy models, then record in Alembic that the database is on the latest migration:

```bash
PYTHONPATH=. python db/scripts/init_mariadb.py
```

```bash
PYTHONPATH=. alembic stamp head
```

- **Later schema changes:** see [Migrations](migrations.md).
- **Start over:** [`drop_mariadb_tables.py`](../utils/mariadb/drop_mariadb_tables.py) drops every table.
- **Check the result:** [`check_mariadb.py`](../db/scripts/check_mariadb.py) lists the tables with their row counts.

## 2. Reference data

Run these four scripts in this order:

| Script                                                                         | Reads                                | Writes                                                 |
|--------------------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------|
| [`load_mariadb_sdg.py`](../utils/mariadb/load_mariadb_sdg.py)                  | `data/icons/` (goal and target SVGs) | 17 SDG goals and 169 targets with colours and icons    |
| [`load_mariadb_sdg_extras.py`](../utils/mariadb/load_mariadb_sdg_extras.py)    | `data/icons/sdg_extras.json`         | Short title, keywords and explanation for each goal    |
| [`load_mariadb_sdg_ranks.py`](../utils/mariadb/load_mariadb_sdg_ranks.py)      | `data/ranks/sdg_ranks.json`          | 4 rank tiers per SDG with name and XP threshold        |
| [`load_mongodb_sdg.py`](../utils/mongodb/load_mongodb_sdg.py)                  | `data/icons/`                        | The same goals and targets in MongoDB                  |

## 3. Users

[`load_mariadb_users.py`](../utils/mariadb/load_mariadb_users.py) creates users with their inventory and roles
(labeler, expert, admin).

Create the accounts defined in `env/users.env`:

```bash
PYTHONPATH=. python utils/mariadb/load_mariadb_users.py
```

The file sets `USER_COUNT`, and for each user `USER_<i>_EMAIL`, `USER_<i>_PASSWORD`, `USER_<i>_ROLE` and
optionally `USER_<i>_NICKNAME`. Users can be numbered from 0 or from 1.

Create 40 generated players:

```bash
PYTHONPATH=. python utils/mariadb/load_mariadb_users.py --generate 40
```

Generated players are labelers with Faker names, e-mail addresses like `<lastname>@example.org`, the password
`password01` and random scores.

> [!NOTE]
> The fixtures (step 11) need at least one user with the `expert` role, so put an expert in `users.env`.

## 4. Publications

[`pipeline/zora/collector.py`](../pipeline/zora/collector.py) harvests publications from the
[ZORA OAI-PMH endpoint](https://www.zora.uzh.ch/cgi/oai2). It stores them with their authors, faculties, institutes
and divisions. The limit and paths are in `CollectorSettings`.

```bash
PYTHONPATH=. python pipeline/zora/collector.py --db mariadb --reset false --recreate_organizational_structure true
```

| Option                                | Meaning                                                                       |
|---------------------------------------|-------------------------------------------------------------------------------|
| `--db mariadb`                        | Target database (the default, `sqlite`, is not used by the application)       |
| `--reset true`                        | **Drops and recreates every MariaDB table** before harvesting                 |
| `--recreate_organizational_structure` | Rebuild faculties, institutes and divisions from `ListSets`                   |
| `--from-dir <folder>`                 | Read `ListSets.xml`, `ListRecords.xml` and one file per resumption token from a folder instead of ZORA (used by the dummy dataset) |

## 5. SDG predictions

Maps, levels and quests use the predictions of a single model, `DEFAULT_PREDICTION_MODEL` in `MariaDBSettings`.
Choose it with the environment variable `PREDICTION_MODEL`:

- `Aurora` (the default): the thesis dataset
- `Dvdblk`: the dummy dataset

`docker-compose.yml` passes the variable to the `api` container. For the scripts, set it in your shell.

### Aurora (thesis dataset)

[`aurora_model_loader.py`](../pipeline/zora/aurora_model_loader.py) downloads the pretrained
[Aurora](https://aurora-universities.eu/) SDG models from Zenodo into `data/pipeline/aurora_models/`. The download
links are in [`aurora-model-goal-only-links.csv`](../pipeline/zora/aurora-model-goal-only-links.csv). Then:

| Script                                                                         | Result                                                                  |
|--------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| [`predictor.py`](../pipeline/zora/predictor.py)                                | One score per SDG goal and publication (`prediction_model = "Aurora"`)  |
| [`target_predictor.py`](../pipeline/zora/target_predictor.py)                  | Scores for the SDG targets                                              |

Both take `--db mariadb --batch_size <n> --mariadb_batch_size <n>`.

> [!IMPORTANT]
> The Aurora models are Keras models and need **TensorFlow 2.11**. TensorFlow is not part of the Poetry environment;
> it is commented out in [`pipeline/pyproject.toml`](../pipeline/pyproject.toml). Run the two predictors in an
> environment that has TensorFlow 2.11 installed.

### SciBERT (dummy dataset)

[`predictor_dvdblk.py`](../pipeline/zora/predictor_dvdblk.py) predicts the goals with the PyTorch model
[`dvdblk/scibert_sdg_cased_zo-up`](https://huggingface.co/dvdblk/scibert_sdg_cased_zo-up) and stores them with
`prediction_model = "Dvdblk"`. On first use, the model is downloaded to `data/pipeline/model/scibert_sdg_classification`
([`utils/sdg_predictor.py`](../utils/sdg_predictor.py)). The SDG explanations from SDG-Scout were computed with this
model. The script only predicts publications that do not have a `Dvdblk` prediction yet.

```bash
PYTHONPATH=. python pipeline/zora/predictor_dvdblk.py --db mariadb
```

### Uncertainty

| Script                                                                                             | Result                                                              |
|----------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| [`load_mariadb_sdg_predictions_entropy.py`](../utils/mariadb/load_mariadb_sdg_predictions_entropy.py) | Entropy and standard deviation of every prediction (used as uncertainty) |
| [`load_mariadb_scaler.py`](../utils/mariadb/load_mariadb_scaler.py)                                 | Optional experiment: rescaled copies (`Scaled_Aurora`), limited to 5 |

A publication belongs to an SDG if its score reaches `DEFAULT_PREDICTION_THRESHOLD` (0.98) in `MariaDBSettings`.

Two other experiments are kept for reference: [`predictor_bielik.py`](../pipeline/zora/predictor_bielik.py) and
[`fine_tune.py`](../pipeline/aurora/fine_tune.py), which fine-tunes the Aurora models.

## 6. Embeddings

[`pipeline/zora/loader.py`](../pipeline/zora/loader.py) embeds `"Title: … Abstract: …"` of every publication with
`sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). It stores the vectors in the Qdrant collection
`publications-mt`, with the MariaDB ID in the payload field `sql_id`.

```bash
PYTHONPATH=. python pipeline/zora/loader.py --db mariadb --batch_size 64
```

## 7. Maps (UMAP)

The exploration maps show publications as points in 2D. The coordinates are stored as dimensionality reductions.

| Script                                                                                | What it projects                                                                                                                                  |
|---------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| [`load_mariadb_umap.py`](../utils/mariadb/load_mariadb_umap.py)                       | Per SDG, 3 **levels** by prediction score: 1.0–0.98, 0.98–0.9 and 0.9–0.7 (`FILTER_RANGES`). Maps with fewer than 5 publications are skipped. Saves one model per SDG and level to `data/api/umap_model/config_15_0.0_2/`. |
| [`load_mariadb_umap_complete.py`](../utils/mariadb/load_mariadb_umap_complete.py)     | All publications, split into partitions, stored as `SDG0-level<n>`                                                                                |
| [`pipeline/zora/reducer.py`](../pipeline/zora/reducer.py)                             | The pipeline version of the same step                                                                                                             |

The UMAP parameters (`n_neighbors=15`, `min_dist=0.0`, `n_components=2`) are in `ReducerSettings`. The API loads the
saved models from `data/api/umap_model/` to place new points on a map. Restart the API after new models were written.

## 8. Topics and clusters

### Collections

Collections are the topics shown on the overview map. Three scripts create them:

1. [`generate_umap_with_tm.py`](../utils/mariadb/generate_umap_with_tm.py) fits a
   [BERTopic](https://maartengr.github.io/BERTopic/) model on all embeddings from Qdrant, using HDBSCAN, c-TF-IDF and
   the SDG descriptions as seed words. It reduces the model to 20 topics plus an outlier topic and writes
   `uzh_topic_data.csv` and `uzh_topic_info.csv` to `data/pipeline/collections/`.
   [`generate_topic_model.py`](../utils/mariadb/generate_topic_model.py) is an earlier version, and
   [`notebooks/topic_model.ipynb`](../notebooks/topic_model.ipynb) is the exploration.
2. [`simplify_topic_info.py`](../utils/mariadb/simplify_topic_info.py) adds a short readable name per topic
   (`GPT_Name`) and writes `uzh_topic_info_simplified.csv`. For the thesis dataset these names were written with
   ChatGPT; the script builds them from each topic's two top keywords.
3. [`load_mariadb_collections.py`](../utils/mariadb/load_mariadb_collections.py) loads the topics as collections and
   their 2D positions as reductions with the shorthand `TM-UZH-UMAP-15-0.0-2`.

### Clusters

Clusters are prepared per SDG, with 25 levels of 1 to 25 topics each. They come from SDG-Scout and were not used in
the deployed version.

| Script                                                                                            | Reads                                   | Writes                                     |
|---------------------------------------------------------------------------------------------------|-----------------------------------------|--------------------------------------------|
| [`load_mariadb_clusters.py`](../utils/mariadb/load_mariadb_clusters.py)                           | `data/db/full_dataset_clusters.json`    | Cluster groups, levels and topics          |
| [`load_mariadb_clusters_publications.py`](../utils/mariadb/load_mariadb_clusters_publications.py) | `data/db/publications_clusters.txt`     | Publication-to-cluster assignments         |
| [`load_mongodb_clusters.py`](../utils/mongodb/load_mongodb_clusters.py)                           | `data/db/full_dataset_clusters.json`    | The same clusters in MongoDB               |

## 9. Ground-truth labels

[`load_mariadb_sdg_label_summaries.py`](../utils/mariadb/load_mariadb_sdg_label_summaries.py) reads
`data/db/sdg_label_summary.txt`. The file holds SQL-style tuples `(publication, sdg1, …, sdg17)`, with `1` for the
correct SDG; the publication is a MariaDB ID or an OAI identifier. For each tuple, the script creates a label summary
and a label history. The fixtures use these labels as the truth when they simulate votes. The labels come from
SDG-Scout.

## 10. Explanations

The explanations show which words of an abstract point to an SDG. They were computed in SDG-Scout and are stored in
the MongoDB database `sdg_explanations`:

1. Split the export into files of 10,000 lines with
   [`sdg-explanation-splitter.sh`](../utils/mongodb/sdg-explanation-splitter.sh) (run it next to
   `sdg_explanations.json`) and put the parts in `data/db/explanations/`.
2. [`load_mongodb_explanations.py`](../utils/mongodb/load_mongodb_explanations.py) loads them into the collection
   `explanations`.
3. [`load_mongodb_small_explanations.py`](../utils/mongodb/load_mongodb_small_explanations.py) stores the token
   scores as integers (× 10,000), which makes them about 30 % smaller. It writes the collection the API reads,
   `explanations_scaled_new` (`MongoDBSDGSettings.DB_COLLECTION_NAME`), and replaces it on every run.

[`debug_mongo.py`](../utils/mongodb/debug_mongo.py) removes duplicate explanations.

## 11. Fixtures: simulated game activity

[`load_mariadb_fixtures.py`](../utils/mariadb/load_mariadb_fixtures.py) fills the game tables so the application
looks like it has been played. It needs users (at least one expert), publications, label summaries and label
histories.

```bash
PYTHONPATH=. python utils/mariadb/load_mariadb_fixtures.py --no-gpt
```

| Option                   | Meaning                                                                                       |
|--------------------------|-----------------------------------------------------------------------------------------------|
| `--no-gpt`               | Write comments and annotations with Faker instead of the OpenAI API (free and offline)       |
| `--max-publications <n>` | Publications with a ground-truth label that get a scenario (default: 500)                    |

> [!WARNING]
> Without `--no-gpt`, GPT writes every comment and annotation. That needs `OPENAI_API_KEY` in `env/api.env`, costs
> money and takes a while. In both modes, the script first **truncates** the tables for user labels, votes,
> annotations, label decisions, wallets and XP banks.

The script works in four stages:

1. **Personas.** Each user gets a temporary
   [Bartle player type](https://en.wikipedia.org/wiki/Bartle_taxonomy_of_player_types) (Achiever, Explorer,
   Socializer or Killer), a trust score, an interest and a skill
   ([`personas_generator.py`](../utils/personas/personas_generator.py)). Personas are not stored.
2. **Wallets and XP banks** for every user, with 5 history entries each.
3. **Scenario decisions.** For each publication with a ground-truth label, it picks a scenario and creates
   `VOTES_NEEDED_FOR_SCENARIO` (10) user labels whose distribution matches the scenario. The true SDG always wins or
   is part of the tie.

   | Scenario    | Distribution of the 10 votes        |
   |-------------|-------------------------------------|
   | Confirm     | 90 % true SDG, 10 % another SDG     |
   | Tiebreaker  | 50 % true SDG, 50 % another SDG     |
   | Investigate | 3 / 3 / 3 / 1                       |
   | Explore     | 1 / 2 / 2 / 2 / 1 / 1 / 1           |

4. **Comments and annotations** in the voice of each user's persona
   ([`persona_comment_generator_strategy.py`](../services/gpt/strategies/persona_comment_generator_strategy.py)).

The ratios are in `FixturesSettings` and the vote thresholds in `DecisionServiceSettings`. `populate_db()` also
contains older random generators for user labels, votes, annotations and decisions; they are switched off with
`if False:`.


## GPT evaluation datasets (optional)

The application does not need these scripts. They build the datasets for the thesis evaluation of how well GPT agrees
with the model predictions. They read publications that have a ground-truth label, call the OpenAI API (which costs
money), and write CSV files into the current directory.

| Script                                                                                            | Output                                    | What it asks GPT                                                                                   |
|---------------------------------------------------------------------------------------------------|-------------------------------------------|----------------------------------------------------------------------------------------------------|
| [`generate_confidence_score.py`](../utils/dataset/generate_confidence_score.py)                   | `chatgpt_sdg_classification_results.csv`  | An initial SDG guess with reasoning and confidence, then an assessment of the model's prediction   |
| [`chatgpt_dataset_generation.py`](../utils/dataset/chatgpt_dataset_generation.py)                 | `sdg_evaluation_results_with_costs.csv`   | Relevance and confidence for all 17 SDGs, arguments for and against one SDG, and the estimated cost |
| [`chatgpt_dataset_generation_batchify.py`](../utils/dataset/chatgpt_dataset_generation_batchify.py) | `batch_results.csv`                     | The same, through the cheaper OpenAI Batch API                                                     |

The number of publications per SDG is set in each script: `LIMIT` or `.limit()` in the query, or `no_samples`.
