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
  - [x] Optional abstracts written by a local model (`--mode ollama`, free) or by Claude (`--mode llm`, paid)
- [x] Load it with the regular pipeline (`utils/dummy/load_dummy_dataset.py`, one command) and test end to end in an
  isolated Docker network: collector, Dvdblk predictions, Qdrant, UMAP, BERTopic, loaders, fixtures, API, frontend
- [x] Document in the README how to load the dummy dataset
- [ ] Generate the dataset with `--mode ollama` (free, about 6 hours for 600 papers) or `--mode llm` (costs money);
  both give better topics than the template abstracts
- [ ] Publish the generator repository on GitHub
- [ ] SDG clusters (`full_dataset_clusters.json`) are not generated; they were not used in the deployed version
- [x] UZH data in the notebooks: decided (2026-09-24) to keep the notebooks as they are. They are part of the thesis
  analysis and contain titles and abstracts (no full papers), which are also public on ZORA. The dataset itself
  (`data/`) stays unpublished.
  - `notebooks/topic_model.ipynb` and `notebooks/topic_data.json`: titles and abstracts
  - `notebooks/exploration.ipynb`: titles in Plotly outputs; `notebooks/publication_comparison.ipynb`: ZORA
    identifiers and titles; `notebooks/model_comparison.ipynb`: no publication data

## 2. Update the API collection (via openapi.json)

- [x] Regenerate the collection from `http://localhost:1002/openapi.json` with Postman's converter
  (`openapi-to-postmanv2`) and `docs/api/finalize_postman_collection.py`: all 111 requests, variables, Bearer auth,
  login test script, no passwords or tokens
- [x] Document the steps in `docs/api/README.md`

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
- [x] Fix `deploy/frontend.prod.Dockerfile`: npm lockfile, Node 20, larger build heap, API address at runtime
  (`NUXT_PUBLIC_API_URL`); tested with the running API. A `.dockerignore` keeps `data/` out of the build context
- [x] Start page and `/login`: use the existing `none` layout (was `empty`, which does not exist)
- [x] Clean up build warnings: duplicated auto-import `createBarPlot` (unused `barPlot.ts` removed), missing
  `assets/icons/` components directory, `defineProps`/`defineEmits` imports, `size="sm"` on `UCheckbox`, chunk size
  warning for Plotly. Only the outdated Browserslist data remains (updating it changes the lockfile)
- [x] Remove `nuxt-app/` (empty starter)
- [x] Lint and format the Python code with Ruff (`ruff.toml`); fixed on the way: two `Config` classes in
  `schemas/gpt_assistant_service.py` were not indented into their schema
- [ ] Unused local variables (Ruff F841, about 110) are ignored for now; clean them up when touching the code
- [ ] Fix the ESLint findings (`npm run lint`: about 380, of which `npm run lint:fix` fixes about 260)

## 4. Fix the dataset scripts

- [x] Fix outdated imports in `pipeline/zora/*.py` (`models.publication`, `models.author`, `models.sdg_label`, …)
- [x] Fix `models.sdg.*` imports in `utils/mariadb/load_mariadb_sdg.py` and the cluster loaders
- [x] Remove the unused `ExplainerSettings` from the scripts in `utils/dataset/`
- [x] Restore `pipeline/zora/predictor_dvdblk.py` from the first commit (it had been overwritten with `collector.py`)
- [x] Align the MongoDB collection names: the scaled explanations are written to `explanations_scaled_new`
- [x] Reducer: use `is_dim_reduced` and set `sdg`/`level` (required columns)
- [ ] Aurora predictors need TensorFlow 2.11: add it to `pipeline/pyproject.toml` (or a separate environment) and
  test `predictor.py` / `target_predictor.py`
- [x] Wrap the loader scripts in `main()` functions (19 scripts ran on import, some dropped their database);
  verified with a full dummy run and by importing the MongoDB loaders without effect
- [x] Run the whole dataset build end to end with the dummy dataset. Fixed on the way: Qdrant rejected the collector's
  placeholder prediction (silently), UMAP level numbering after skipped ranges, BERTopic `min_df` for few topics,
  required SDG columns, API crashing without CouchDB/Redis
- [x] Prediction model configurable (`PREDICTION_MODEL`, default Aurora) instead of hardcoded "Aurora"
- [x] Remove the `pipeline` and `prefect` containers: all scripts run on the host in the `pipeline/pyproject.toml`
  environment (now also with Faker, Instructor and Alembic); the dummy dataset loads with one command

## 5. Other cleanup

- [x] Stop logging the plaintext password on a failed login (`api/app/routes/authentication.py`); tokens are no longer logged either
- [x] Return 401 instead of 500 when a token is invalid (e.g. `GET /sdgs`, `/banks/latest`, `/wallets/latest` wrap the
  `HTTPException` in a 500)
- [x] Remove the `backend` service from `docker-compose.yml` (the `backend/` folder no longer exists)
- [x] Update the port table in `docs/docker.md`
- [x] Remove CouchDB and Redis (containers, connectors, dependencies, docs); no feature used them
- [x] Add an example env file for `portainer.env`

## 6. Before publishing

- [ ] Choose and add a license
- [ ] Add the thesis title, link, and supervisors to the README
- [ ] Credit SDG-Scout and the research group
- [x] Check for secrets (2026-09-24): tracked files and the whole git history contain no API keys, JWTs, real
  passwords or env files, only the placeholder values of the `*.env.example` files. The commits carry the UZH
  e-mail addresses `nicolas.huber2@uzh.ch` and `nhuber@ifi.uzh.ch` as author
- [ ] Repeat the check right before publishing, after the notebooks are cleaned
