# TODO

Open tasks before the repository is made public. See also [Known issues](README.md#known-issues).

## 1. Generator repository for a dummy dataset

The original data (UZH publications from ZORA, plus labels, clusters, and explanations from SDG-Scout) cannot be
published.

- [ ] Back up the original `data/` folder (about 24 GB) and keep it outside the repository
- [ ] Create a separate repository with a generator (e.g. Faker) that produces synthetic data in the same formats:
  - [ ] Publications, authors, faculties, institutes, divisions (MariaDB)
  - [ ] SDG predictions (goals and targets)
  - [ ] Embeddings (Qdrant collection `publications-mt`, 384 dimensions)
  - [ ] UMAP coordinates and models (`data/api/umap_model/`)
  - [ ] Topic collections and clusters
  - [ ] Ground-truth labels (`sdg_label_summary.txt`)
  - [ ] SDG explanations (MongoDB `sdg_explanations`)
- [ ] Document in the README how to load the dummy dataset
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
- [ ] Log in and click through all pages (locally and in Docker)
- [ ] Install from the lockfile in `deploy/frontend.Dockerfile` (`npm ci`); the container currently gets Nuxt 3.21
  instead of the locked 3.15
- [ ] Fix `deploy/frontend.prod.Dockerfile` (expects `pnpm-lock.yaml`, final stage uses Node 16)
- [ ] Start page: `layout: 'empty'` does not exist (`layouts/` has `default` and `none`)
- [ ] Start page: the white title disappears in light mode (daisyUI picks the `black` theme from the system setting,
  Nuxt color mode is `light`)
- [ ] Clean up build warnings: duplicated auto-imports `createBarPlot` and `createScatterPlot`, missing
  `assets/icons/` components directory, `defineProps`/`defineEmits` imports
- [ ] Decide what to do with `nuxt-app/` (empty starter)

## 4. Fix the dataset scripts

- [ ] Fix outdated imports in `pipeline/zora/*.py` (`models.publication`, `models.author`, `models.sdg_label`, …)
- [ ] Fix `models.sdg.*` imports in `utils/mariadb/load_mariadb_sdg.py` and the cluster loaders
- [ ] Restore or replace `ExplainerSettings` for the scripts in `utils/dataset/`
- [ ] Mount `models/` and `settings/` in the `pipeline` container
- [ ] Replace `pipeline/zora/predictor_dvdblk.py` (currently a copy of `collector.py`)
- [ ] Align the MongoDB collection names (`explanations_scaled` vs. `explanations_scaled_new`)

## 5. Other cleanup

- [ ] Stop logging the plaintext password on a failed login (`api/app/routes/authentication.py`)
- [ ] Return 401 instead of 500 when a token is invalid (e.g. `GET /sdgs`, `/banks/latest`, `/wallets/latest` wrap the
  `HTTPException` in a 500)
- [ ] Remove the `backend` service from `docker-compose.yml` (the `backend/` folder no longer exists)
- [ ] Update the port table in `docs/docker.md`
- [ ] Add example env files for `portainer.env` and `redisinsight.env`

## 6. Before publishing

- [ ] Choose and add a license
- [ ] Add the thesis title, link, and supervisors to the README
- [ ] Credit SDG-Scout and the research group
- [ ] Last check for secrets (`env/`, Postman, notebooks, git history)
