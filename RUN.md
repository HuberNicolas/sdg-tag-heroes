# Running SDG Tag Heroes (for coding agents)

A short guide for coding agents (Claude Code and others) to get SDG Tag Heroes running in Docker with the synthetic
dataset. The full walkthrough for people is [Dummy dataset setup](docs/dummy-dataset.md); this file lists the fastest
path, the checks and the pitfalls found while setting it up.

Both repositories are expected side by side: `sdg-tag-heroes/` and `sdg-tag-heroes-dataset-generator/`.

## 0. Check first: is it already running?

```bash
docker compose ps --format '{{.Name}} {{.Status}}'
```

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:1002/docs
```

If `data/docker/` exists, the databases are already filled. Start the containers and stop here; do **not** rebuild the
dataset:

```bash
docker compose up -d api mariadb mongodb qdrantdb frontend
```

Frontend: <http://localhost:3030>, API: <http://localhost:1002/docs>.

## 1. Prerequisites

| Tool                   | Check                     | Install                                      |
|------------------------|---------------------------|----------------------------------------------|
| Docker with Compose v2 | `docker compose version`  | –                                            |
| uv                     | `uv --version`            | –                                            |
| Poetry                 | `poetry --version`        | `uv tool install poetry`                     |
| Python 3.10.14         | `uv python find 3.10.14`  | `uv python install 3.10.14`                  |
| C compiler (`hdbscan`) | `gcc --version`           | `build-essential` or Xcode Command Line Tools |
| Ollama (optional)      | `ollama list`             | only for realistic abstracts                 |

Ports 1002, 2001–2003 and 3030 must be free. Start only the services named below, not `--profile prod`: the container
names are fixed, and a `portainer` container that already runs on the machine would clash with the one of this stack.

## 2. Generate the dataset

In `sdg-tag-heroes-dataset-generator/`:

```bash
uv sync
```

Fast (seconds; template abstracts, BERTopic finds only one or two topics):

```bash
uv run sdg-dummy-data --count 340 --out output
```

Realistic (a local model; on a CPU about one minute per paper with `llama3.1`, so several hours):

```bash
uv run sdg-dummy-data --count 340 --out output --mode ollama --model llama3.1
```

- The guide recommends about 600 papers; with far fewer, many SDGs have too few papers for a map. 340 (20 per SDG)
  was tested and works.
- Finished papers are cached in `output/cache/papers-<mode>.jsonl`, so a stopped run resumes. Rerun with the **same
  `--count` and `--seed`**: authors, faculties, years and topics depend on `--count`, so a cache written for another
  count does not match.
- Run long generations in the background and in a retry loop; each rerun continues from the cache.
- Prefer `llama3.1` or `llama3.2`. `gemma3` repeats itself inside the JSON answer and is very slow.

## 3. Set up SDG Tag Heroes

In `sdg-tag-heroes/`:

```bash
mkdir -p data/api && cp -R ../sdg-tag-heroes-dataset-generator/output/data/. data/
```

```bash
python3 utils/docker/create_env_files.py --dummy-dataset
```

```bash
grep -q NUXT_PUBLIC_MAP_PARTITIONS frontend/.env || echo "NUXT_PUBLIC_MAP_PARTITIONS=3" >> frontend/.env
```

`create_env_files.py` never overwrites a file. The account passwords are in `env/users.env`; do not print them into
the conversation or logs. To log in to the frontend for a test, use a generated player instead: `<lastname>@example.org`
with the password `password01`. Find an e-mail address with:

```bash
docker compose exec -T mariadb sh -c 'mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" igcl -N -e "SELECT email FROM users WHERE email LIKE \"%@example.org\" LIMIT 1"'
```

Start the databases and the API (the first build takes several minutes):

```bash
docker compose up -d --build api mariadb mongodb qdrantdb
```

```bash
docker compose exec mariadb sh -c 'until mariadb-admin ping -u root -p"$MYSQL_ROOT_PASSWORD" --silent; do sleep 2; done'
```

Set up the Python environment of the dataset scripts:

```bash
poetry -C pipeline env use "$(uv python find 3.10.14)"
```

```bash
poetry -C pipeline install --no-root
```

Run the pipeline (10–30 minutes on a CPU; `topics` (BERTopic) is the slowest step, especially while Ollama runs):

```bash
source "$(poetry -C pipeline env info --path)/bin/activate" && PYTHONPATH=. python utils/dummy/load_dummy_dataset.py
```

Then load the new UMAP models and start the frontend:

```bash
docker compose restart api
```

```bash
docker compose up -d --build frontend
```

## 4. Check the result

```bash
docker compose exec -T mariadb sh -c 'mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" igcl -e "SELECT (SELECT COUNT(*) FROM publications) publications, (SELECT COUNT(*) FROM dimensionality_reductions) map_points, (SELECT COUNT(*) FROM collections) topics, (SELECT COUNT(*) FROM users) users, (SELECT COUNT(*) FROM sdg_label_decisions) decisions"'
```

```bash
curl -s -X POST http://localhost:2003/collections/publications-mt/points/count -H 'Content-Type: application/json' -d '{}'
```

With 340 papers: 340 publications, 340 Qdrant points, about 1100 map points, 300 decisions and about 40 users. In the
browser: log in, then `/profile`, `/scenarios`, and choose an SDG.

## 5. Load another dataset

`load_dummy_dataset.py` only loads into **empty** databases. `data/docker/` is owned by root, and
`utils/docker/delete-docker-data.sh` uses `sudo`. Without `sudo`, delete it through a container:

```bash
docker compose down
```

```bash
docker run --rm -v "$PWD/data:/d" alpine rm -rf /d/docker
```

```bash
rm -rf data/api/umap_model data/pipeline/collections data/pipeline/oai data/db/explanations
```

Then copy the new data (step 3) and continue with `docker compose up -d …` (without `--build` if the images exist).

## Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `mongodb-database` keeps restarting: "Linux kernel versions 6.19 and newer has a known incompatibility" | MongoDB 8.x (TCMalloc and rseq, SERVER-121912) | `deploy/db/mongodb.Dockerfile` pins `mongo:7.0`; do not change it to `latest`. MongoDB 7.0 cannot read data files written by 8.x, so start from an empty `data/docker/db/mongodb/` |
| `poetry install`: "Hash for nvidia-… not found in known hashes" | A truncated wheel in the Poetry cache | Delete it (`find ~/.cache/pypoetry -name 'nvidia_…*'`) and install again |
| `AttributeError: module 'bcrypt' has no attribute '__about__'` in the `users` steps | passlib with a newer bcrypt | A harmless, trapped warning; the users are created |
| The frontend shows "Starting Nuxt…" or a white page, or the login form empties itself | Nuxt and Vite compile each route on its first visit and reload | Wait 10–30 seconds and try again |
| The login API answers nothing right after `docker compose restart api` | The API is still starting | Wait a few seconds |
| An SDG (often 17) has no map | SciBERT rarely scores it above 0.7 | Expected |
