"""
Build the dummy dataset from the output of sdg-tag-heroes-dataset-generator, using the regular dataset scripts.

The generator replaces ZORA (OAI-PMH files in data/pipeline/oai) and SDG-Scout (ground-truth labels and
explanations in data/db). Everything else is computed by the existing scripts, one after the other:

    schema -> collector (from files) -> SDG predictions (Dvdblk) -> entropy -> embeddings (Qdrant) -> UMAP maps
    -> BERTopic topics -> SDGs, ranks, users, labels, topic collections, explanations (MongoDB) -> simulated players

Copy the generator's output/data/ into data/ first, start the databases, then run from the repository root in the
Poetry environment of pipeline/pyproject.toml:
    PYTHONPATH=. python utils/dummy/load_dummy_dataset.py

Several scripts drop or truncate what they fill. The run therefore only starts on empty databases, and a resumed run
(--from-step) only when every publication in MariaDB is a dummy publication.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OAI_DIR = "data/pipeline/oai"
DUMMY_OAI_PREFIX = "oai:dummy."
PREDICTION_MODEL = "Dvdblk"

# (name, script, arguments), in order
STEPS = [
    ("schema", "db/scripts/init_mariadb.py", []),
    ("collector", "pipeline/zora/collector.py",
     ["--db", "mariadb", "--recreate_organizational_structure", "true", "--from-dir", OAI_DIR]),
    ("predictions", "pipeline/zora/predictor_dvdblk.py", ["--db", "mariadb"]),
    ("entropy", "utils/mariadb/load_mariadb_sdg_predictions_entropy.py", []),
    ("embeddings", "pipeline/zora/loader.py", ["--db", "mariadb"]),
    ("umap", "utils/mariadb/load_mariadb_umap.py", []),
    ("topics", "utils/mariadb/generate_umap_with_tm.py", []),
    ("topic-names", "utils/mariadb/simplify_topic_info.py", []),
    ("sdgs", "utils/mariadb/load_mariadb_sdg.py", []),
    ("sdg-extras", "utils/mariadb/load_mariadb_sdg_extras.py", []),
    ("ranks", "utils/mariadb/load_mariadb_sdg_ranks.py", []),
    ("users", "utils/mariadb/load_mariadb_users.py", []),
    ("players", "utils/mariadb/load_mariadb_users.py", ["--generate", "40"]),
    ("labels", "utils/mariadb/load_mariadb_sdg_label_summaries.py", []),
    ("collections", "utils/mariadb/load_mariadb_collections.py", []),
    ("mongo-sdgs", "utils/mongodb/load_mongodb_sdg.py", []),
    ("explanations", "utils/mongodb/load_mongodb_explanations.py", []),
    ("explanations-scaled", "utils/mongodb/load_mongodb_small_explanations.py", []),
    ("fixtures", "utils/mariadb/load_mariadb_fixtures.py", ["--no-gpt", "--max-publications", "300"]),
]


def database_problems(resume: bool) -> list[str]:
    """Reasons why the run must not touch the connected databases."""
    sys.path.insert(0, str(REPO_ROOT))
    from sqlalchemy import inspect, text

    from db.mariadb_connector import engine

    publications = other = 0
    if "publications" in inspect(engine).get_table_names():
        with engine.connect() as connection:
            publications = connection.execute(text("SELECT COUNT(*) FROM publications")).scalar()
            other = connection.execute(
                text("SELECT COUNT(*) FROM publications WHERE oai_identifier NOT LIKE :prefix"),
                {"prefix": DUMMY_OAI_PREFIX + "%"},
            ).scalar()

    if resume:
        return [f"MariaDB contains {other} publications that are not from the dummy dataset"] if other else []

    from db.qdrantdb_connector import client as qdrant_client
    from settings.settings import QdrantDBSettings

    problems = []
    if publications:
        problems.append(f"MariaDB already contains {publications} publications")
    collection = QdrantDBSettings.PUBLICATIONS_COLLECTION_NAME
    if qdrant_client.collection_exists(collection) and qdrant_client.count(collection).count:
        problems.append(f"Qdrant collection '{collection}' is not empty")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-step", help="resume at this step")
    parser.add_argument("--gpt", action="store_true", help="let GPT write the simulated comments (costs money)")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)
    if not Path(OAI_DIR, "ListRecords.xml").exists():
        raise SystemExit(f"{OAI_DIR}/ListRecords.xml not found. Copy the generator's output/data/ into data/ first.")

    steps = STEPS
    names = [name for name, _, _ in steps]
    if args.from_step:
        if args.from_step not in names:
            raise SystemExit(f"Unknown step: {args.from_step} (steps: {', '.join(names)})")
        steps = steps[names.index(args.from_step):]
    if problems := database_problems(resume=bool(args.from_step)):
        raise SystemExit("Refusing to load the dummy dataset:\n  - " + "\n  - ".join(problems))

    # Maps, levels and quests use the Dvdblk predictions (settings.MariaDBSettings.DEFAULT_PREDICTION_MODEL)
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT), "PREDICTION_MODEL": PREDICTION_MODEL}
    # PyTorch parallelises itself; nested OpenBLAS threads only compete with it and slow the predictor down
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    for name, script, script_args in steps:
        if name == "fixtures" and args.gpt:
            script_args = [a for a in script_args if a != "--no-gpt"]
        print(f"\n=== {name}: {script} {' '.join(script_args)}", flush=True)
        start = time.time()
        if subprocess.run([sys.executable, script, *script_args], env=env).returncode != 0:
            raise SystemExit(f"Step '{name}' failed. Fix it and resume with --from-step {name}")
        print(f"=== {name} done in {time.time() - start:.0f}s", flush=True)

    print("\nDummy dataset loaded. Start the API with PREDICTION_MODEL=Dvdblk so it uses the Dvdblk predictions.")


if __name__ == "__main__":
    main()
