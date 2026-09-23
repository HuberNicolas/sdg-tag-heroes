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

- [ ] Decide between `frontend2/` (working: Nuxt UI 2, Tailwind 3, daisyUI 4) and `frontend/` (unfinished upgrade:
  Nuxt UI 3, Tailwind 4, daisyUI 5)
- [ ] Compare the files that differ (`app.vue`, `pages/labeling/[publicationId].vue`, configs) and keep any newer changes
- [ ] Keep one folder named `frontend/` and archive the other
- [ ] Update the `frontend` service in `docker-compose.yml` and `deploy/frontend*.Dockerfile`
  (`frontend.prod.Dockerfile` expects a `pnpm-lock.yaml`)
- [ ] Decide what to do with `nuxt-app/` (empty starter)
- [ ] Update the README

## 4. Fix the dataset scripts

- [ ] Fix outdated imports in `pipeline/zora/*.py` (`models.publication`, `models.author`, `models.sdg_label`, …)
- [ ] Fix `models.sdg.*` imports in `utils/mariadb/load_mariadb_sdg.py` and the cluster loaders
- [ ] Restore or replace `ExplainerSettings` for the scripts in `utils/dataset/`
- [ ] Mount `models/` and `settings/` in the `pipeline` container
- [ ] Replace `pipeline/zora/predictor_dvdblk.py` (currently a copy of `collector.py`)
- [ ] Align the MongoDB collection names (`explanations_scaled` vs. `explanations_scaled_new`)

## 5. Other cleanup

- [ ] Stop logging the plaintext password on a failed login (`api/app/routes/authentication.py`)
- [ ] Remove the `backend` service from `docker-compose.yml` (the `backend/` folder no longer exists)
- [ ] Update the port table in `docs/docker.md`
- [ ] Add example env files for `portainer.env` and `redisinsight.env`

## 6. Before publishing

- [ ] Choose and add a license
- [ ] Add the thesis title, link, and supervisors to the README
- [ ] Credit SDG-Scout and the research group
- [ ] Last check for secrets (`env/`, Postman, notebooks, git history)
