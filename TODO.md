# TODO

Open tasks before the repository is made public. See also [Known issues](README.md#known-issues).

## 1. Generator repository for a dummy dataset

The original data (UZH publications from ZORA, plus labels, clusters, and explanations from SDG-Scout) cannot be
published.

- [ ] Back up the original `data/` folder (about 24 GB) and keep it outside the repository
- [x] Create the generator repository (`../sdg-tag-heroes-dataset-generator`, local only so far). It replaces only the
  external sources; the pipeline computes the rest:
  - [x] ZORA: fictional publications as OAI-PMH files, read with `collector.py --from-dir`
  - [x] SDG-Scout: ground-truth labels and (synthetic) explanations
  - [x] Placeholder SDG icons, SDG texts and rank tiers
  - [x] Optional abstracts written by Claude (`--mode llm`)
- [x] Load it with the regular pipeline (`utils/dummy/load_dummy_dataset.py`, one command) and test end to end in an
  isolated Docker network: collector, Dvdblk predictions, Qdrant, UMAP, BERTopic, loaders, fixtures, API, frontend
- [x] Document in the README how to load the dummy dataset
- [ ] Generate the dataset with `--mode llm` (costs money; better topics than the template abstracts)
- [ ] Publish the generator repository on GitHub
- [ ] SDG clusters (`full_dataset_clusters.json`) are not generated; they were not used in the deployed version
- [ ] Only then: remove UZH data from this repository, including its git history
  - [ ] `notebooks/topic_model.ipynb` (contains ZORA titles and abstracts in cell outputs)
  - [ ] `notebooks/topic_data.json` (contains ZORA titles and abstracts)
  - [ ] Check the other notebooks for publication data

## 2. Update the API collection (via openapi.json)

- [ ] Start the API and import `http://localhost:1002/openapi.json` into Postman
- [ ] Add the 14 endpoints that are missing from the current collection (listed in
  [`docs/api/README.md`](docs/api/README.md#endpoints-not-yet-in-the-collection))
- [ ] Restore the variables (`baseUrl`, `email`, `password`, `bearerToken`) and the login test script
- [ ] Export as Collection v2.1 to `docs/api/sdg-tag-heroes.postman_collection.json` and check it for passwords and tokens
- [ ] Optionally commit a static `docs/api/openapi.json`

## 3. Clean up the frontend

- [x] Decide between `frontend2/` and `frontend/`: kept `frontend2/` (Nuxt UI 2, Tailwind 3, daisyUI 4). The upgrade
  to Nuxt UI 3 / Tailwind 4 / daisyUI 5 had only changed the configs; 24 components still used the old API.
- [x] Compare the files that differ: only configs, `app.vue`, and one unused import
- [x] Keep one folder named `frontend/`; the upgrade is on the branch `archive/frontend-nuxt-ui-3`
- [x] Docker `frontend` service runs the working frontend; HMR port only set in Docker (`HMR_CLIENT_PORT`)
- [x] Update the README
- [x] Log in and click through all pages (Docker, at 1280, 1920 and 3440 px)
- [x] Responsive layout for laptop to ultrawide (1280–3440 px): base layout, navigation, scenarios, exploration,
  labeling; charts follow their container (`useRedrawOnResize`)
- [x] Fix bugs found on the way: map data joined by index, quest selection looping, labeling arrows pointing at
  removed elements, `/scenarios` store imports, production build (`nuxi build`) failing
- [x] Remove broken legacy pages (`/publications`, `/publications/[id]`), replace `/about` test page
- [ ] Tablet and phone layouts (not planned so far; visualisations need space)
- [x] Install from the lockfile in `deploy/frontend.Dockerfile` (`npm ci`); newer packages (Nuxt 3.21, Nuxt UI 2.22)
  broke the layout. Do not upgrade the frontend packages without checking the layout.
- [ ] Fix `deploy/frontend.prod.Dockerfile` (expects `pnpm-lock.yaml`, final stage uses Node 16)
- [x] Start page and `/login`: use the existing `none` layout (was `empty`, which does not exist)
- [ ] Clean up build warnings: duplicated auto-import `createBarPlot`, missing `assets/icons/` components
  directory, `defineProps`/`defineEmits` imports, `size="sm"` on a native checkbox (`SDGUserLabelCheckbox`)
- [x] Remove `nuxt-app/` (empty starter)

## 4. Fix the dataset scripts

- [x] Fix outdated imports in `pipeline/zora/*.py` (`models.publication`, `models.author`, `models.sdg_label`, …)
- [x] Fix `models.sdg.*` imports in `utils/mariadb/load_mariadb_sdg.py` and the cluster loaders
- [x] Remove the unused `ExplainerSettings` from the scripts in `utils/dataset/`
- [x] Restore `pipeline/zora/predictor_dvdblk.py` from the first commit (it had been overwritten with `collector.py`)
- [x] Align the MongoDB collection names: the scaled explanations are written to `explanations_scaled_new`
- [x] Reducer: use `is_dim_reduced` and set `sdg`/`level` (required columns)
- [ ] Aurora predictors need TensorFlow 2.11: add it to `pipeline/pyproject.toml` (or a separate environment) and
  test `predictor.py` / `target_predictor.py`
- [ ] Wrap the loader scripts in `main()` functions: many run on import and some drop their target database
- [x] Run the whole dataset build end to end with the dummy dataset. Fixed on the way: Qdrant rejected the collector's
  placeholder prediction (silently), UMAP level numbering after skipped ranges, BERTopic `min_df` for few topics,
  required SDG columns, API crashing without CouchDB/Redis
- [x] Prediction model configurable (`PREDICTION_MODEL`, default Aurora) instead of hardcoded "Aurora"
- [x] Remove the `pipeline` and `prefect` containers: all scripts run on the host in the `pipeline/pyproject.toml`
  environment (now also with Faker, Instructor and Alembic); the dummy dataset loads with one command

## 5. Other cleanup

- [ ] Stop logging the plaintext password on a failed login (`api/app/routes/authentication.py`)
- [ ] Return 401 instead of 500 when a token is invalid (e.g. `GET /sdgs`, `/banks/latest`, `/wallets/latest` wrap the
  `HTTPException` in a 500)
- [x] Remove the `backend` service from `docker-compose.yml` (the `backend/` folder no longer exists)
- [x] Update the port table in `docs/docker.md`
- [x] Remove CouchDB and Redis (containers, connectors, dependencies, docs); no feature used them
- [ ] Add an example env file for `portainer.env`

## 6. Before publishing

- [ ] Choose and add a license
- [ ] Add the thesis title, link, and supervisors to the README
- [ ] Credit SDG-Scout and the research group
- [ ] Last check for secrets (`env/`, Postman, notebooks, git history)
