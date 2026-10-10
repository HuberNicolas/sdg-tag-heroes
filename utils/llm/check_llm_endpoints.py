"""
Call every API endpoint that uses the LLM once and report status, time and the start of the answer.

    python3 utils/llm/check_llm_endpoints.py                 # all endpoints
    python3 utils/llm/check_llm_endpoints.py keywords poi    # only checks whose name contains one of the words

Run it against the running stack (API on http://localhost:1002, or --base-url). It logs in with the first account of
env/users.env. Which model answers is set in env/api.env (LLM_PROVIDER, LLM_MODEL; see the README section "Local LLM
with Ollama"). With a local model on a CPU, a single answer takes from a few seconds to a minute or two.

Note: facts and summaries are stored after the first call, so a second run returns them without asking the LLM.
Only the standard library is used.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def first_account() -> tuple[str, str]:
    values = {}
    for line in (REPO_ROOT / "env" / "users.env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"')
    return values["USER_1_EMAIL"], values["USER_1_PASSWORD"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("only", nargs="*", help="run only checks whose name contains one of these words")
    parser.add_argument("--base-url", default="http://localhost:1002", help="address of the API")
    parser.add_argument("--timeout", type=float, default=900, help="seconds to wait for one answer")
    args = parser.parse_args()

    def call(method: str, path: str, body=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(args.base_url + path, method=method, data=data, headers=headers)
        start = time.time()
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                return response.status, json.loads(response.read() or b"null"), time.time() - start
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode()[:300], time.time() - start
        except (urllib.error.URLError, TimeoutError) as error:
            return 0, str(error), time.time() - start

    email, password = first_account()
    status, login, _ = call("POST", "/auth/login", {"email": email, "password": password})
    if status != 200:
        print(f"Login failed ({status}): {login}")
        return 1
    token = login["access_token"]

    # User labels with a comment (and an abstract section) for the comment checks
    _, labels, _ = call("GET", "/user-labels/", token=token)
    labels = labels if isinstance(labels, list) else []
    commented = [label["label_id"] for label in labels if label.get("comment")]
    evaluable = [label["label_id"] for label in labels if label.get("comment") and label.get("abstract_section")]

    checks = [
        ("SDG suggestion from skills", "POST", "/users-profiles/skills/sdgs", {"skills": "I build water filters"}),
        ("SDG suggestion from interests", "POST", "/users-profiles/interests/sdgs", {"interests": "ocean plastic"}),
        ("POI description from skills", "POST", "/users-profiles/skills", {"skills": "I teach maths"}),
        ("POI description from interests", "POST", "/users-profiles/interests", {"interests": "renewable energy"}),
        ("SDG explanation of a publication", "GET", "/publications/3/explain/goal/1", None),
        ("Publication keywords", "GET", "/publications/4/keywords", None),
        ("Did-you-know fact", "GET", "/publications/5/facts", None),
        ("Publication summary", "GET", "/publications/6/summary", None),
        (
            "Summary of several publications",
            "POST",
            "/publications/collective-summaries",
            {"publication_ids": [7, 8, 9]},
        ),
        ("Summary of community comments", "POST", "/user-labels/summary", {"user_labels_ids": commented[:4]}),
        (
            "Annotation score",
            "POST",
            "/annotations/score",
            {
                "passage": "Rising temperatures reduce crop yields.",
                "annotation": "This links to SDG 2 because food production drops.",
                "sdg_label": "sdg2",
            },
        ),
    ]
    if evaluable:
        checks.append(("Evaluation of a label comment", "POST", f"/user-labels/{evaluable[0]}/evaluate", None))

    failed = 0
    for name, method, path, body in checks:
        if args.only and not any(word.lower() in name.lower() for word in args.only):
            continue
        status, result, seconds = call(method, path, body, token)
        text = result if isinstance(result, str) else json.dumps(result)
        ok = status == 200
        failed += not ok
        print(f"{'OK ' if ok else 'ERR'} {status:3} {seconds:6.1f}s  {name}: {text[:160]}", flush=True)

    print(f"\n{'All checks passed.' if not failed else f'{failed} check(s) failed.'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
