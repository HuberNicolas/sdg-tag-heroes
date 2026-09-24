"""
Turn BERTopic's uzh_topic_info.csv into uzh_topic_info_simplified.csv, which load_mariadb_collections.py reads.

It adds the column GPT_Name, a short readable topic name (for the thesis dataset it was written by hand with
ChatGPT). Here it is built from the two most representative keywords of each topic.

Run from the repository root after generate_umap_with_tm.py:
    PYTHONPATH=. python utils/mariadb/simplify_topic_info.py
"""
import ast
import csv
import os

COLLECTIONS_DIR = "./data/pipeline/collections"
SOURCE = os.path.join(COLLECTIONS_DIR, "uzh_topic_info.csv")
TARGET = os.path.join(COLLECTIONS_DIR, "uzh_topic_info_simplified.csv")


def readable_name(row: dict) -> str:
    keywords = [k for k in ast.literal_eval(row["Representation"]) if k]
    if int(row["Topic"]) == -1:
        return "Miscellaneous"
    return " & ".join(k.title() for k in keywords[:2]) or row["Name"]


def main() -> None:
    csv.field_size_limit(10**9)
    with open(SOURCE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    columns = list(rows[0])
    columns.insert(columns.index("Name") + 1, "GPT_Name")
    with open(TARGET, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "GPT_Name": readable_name(row)})
    print(f"Wrote {len(rows)} topics to {TARGET}")


if __name__ == "__main__":
    main()
