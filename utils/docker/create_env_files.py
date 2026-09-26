"""
Create the environment files for a local setup, with random passwords.

    python3 utils/docker/create_env_files.py                  # env/*.env and frontend/.env
    python3 utils/docker/create_env_files.py --dummy-dataset  # also .env with PREDICTION_MODEL=Dvdblk

Every env/<service>.env is created from its env/<service>.env.example. The passwords of MariaDB, MongoDB and
Mongo Express, the JWT secret and the passwords of the initial accounts in users.env are replaced by random values,
and the MongoDB credentials are written consistently into all files that need them. Existing files are never
overwritten, so the script can be run again safely. Only the standard library is used.

The OpenAI API key (env/api.env) stays empty; the application runs without it, only the GPT features fail.
"""

import argparse
import re
import secrets
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_DIR = REPO_ROOT / "env"


def password() -> str:
    # Hex only, so the value is safe in URLs (mongodb://user:password@host) and shell scripts
    return secrets.token_hex(16)


def set_values(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text, count = re.subn(rf"^{re.escape(key)}=.*$", f"{key}={value}", text, flags=re.MULTILINE)
        if not count:
            text += f"\n{key}={value}\n"
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--dummy-dataset",
        action="store_true",
        help="also create .env in the repository root with PREDICTION_MODEL=Dvdblk for docker compose",
    )
    args = parser.parse_args()

    mongo_user, mongo_password = "admin", password()
    users_text = (ENV_DIR / "users.env.example").read_text()
    user_count = int(re.search(r"^USER_COUNT=(\d+)", users_text, re.MULTILINE).group(1))
    user_numbers = sorted({int(n) for n in re.findall(r"^USER_(\d+)_PASSWORD=", users_text, re.MULTILINE)})

    values = {
        "mariadb.env": {
            "MYSQL_ROOT_PASSWORD": password(),
            "MARIADB_USER": "sdg_tag_heroes",
            "MARIADB_PASSWORD": password(),
        },
        "mongodb.env": {
            "MONGO_INITDB_ROOT_USERNAME": mongo_user,
            "MONGO_INITDB_ROOT_PASSWORD": mongo_password,
            "MONGODB_HOST": "mongodb",
        },
        "mongo-express.env": {
            "ME_CONFIG_BASICAUTH_USERNAME": "admin",
            "ME_CONFIG_BASICAUTH_PASSWORD": password(),
            "ME_CONFIG_MONGODB_URL": f"mongodb://{mongo_user}:{mongo_password}@mongodb:27017",
        },
        "backend.env": {"SECRET_KEY": secrets.token_hex(32)},
        "users.env": {f"USER_{n}_PASSWORD": password() for n in user_numbers},
    }

    created, skipped = [], []
    targets = [(example, example.with_suffix("")) for example in sorted(ENV_DIR.glob("*.env.example"))]
    targets.append((REPO_ROOT / "frontend" / ".env.example", REPO_ROOT / "frontend" / ".env"))
    for example, target in targets:
        if target.exists():
            skipped.append(target)
            continue
        text = example.read_text()
        text = set_values(text, values.get(target.name, {}))
        target.write_text(text)
        created.append(target)

    if args.dummy_dataset:
        root_env = REPO_ROOT / ".env"
        if root_env.exists():
            skipped.append(root_env)
        else:
            root_env.write_text(
                "# Read by docker compose: the dummy dataset uses the predictions of the Dvdblk model\n"
                "PREDICTION_MODEL=Dvdblk\n"
            )
            created.append(root_env)

    for path in created:
        print(f"created  {path.relative_to(REPO_ROOT)}")
    for path in skipped:
        print(f"kept     {path.relative_to(REPO_ROOT)} (exists already)")

    users_env = ENV_DIR / "users.env"
    if users_env in created:
        text = users_env.read_text()
        print(f"\nAccounts in env/users.env ({user_count}):")
        for n in user_numbers:
            email = re.search(rf"^USER_{n}_EMAIL=(.*)$", text, re.MULTILINE).group(1)
            secret = re.search(rf"^USER_{n}_PASSWORD=(.*)$", text, re.MULTILINE).group(1)
            role = re.search(rf"^USER_{n}_ROLE=(.*)$", text, re.MULTILINE).group(1)
            print(f"  {email:<24} {secret}  ({role})")


if __name__ == "__main__":
    main()
