"""
Turn the Postman collection converted from the API's openapi.json into the collection in this folder.

    npx openapi-to-postmanv2@4 -s openapi.json -o converted.json -p -O folderStrategy=Paths
    python3 docs/api/finalize_postman_collection.py converted.json docs/api/sdg-tag-heroes.postman_collection.json

The converter nests one folder per path segment. This script groups the requests by their first path segment, lets
every request inherit the collection's Bearer auth, fills the login body from variables, and adds the test script
that stores the token. It removes the converter's random IDs, so a regenerated collection only differs where the API
changed. Only the standard library is used.
"""
import json
import sys

DESCRIPTION = (
    'All endpoints of the SDG Tag Heroes FastAPI backend. Run "auth/login" first: it stores the JWT in the collection '
    "variable bearerToken, which every other request uses. See docs/api/README.md."
)
VARIABLES = [
    {"key": "baseUrl", "value": "http://localhost:1002", "type": "string"},
    {"key": "email", "value": "labeler@tagheroes.ch", "type": "string"},
    {"key": "password", "value": "", "type": "string"},
    {"key": "bearerToken", "value": "", "type": "string"},
]
LOGIN_TEST = [
    "if (pm.response.code === 200) {",
    '  pm.collectionVariables.set("bearerToken", pm.response.json().access_token);',
    "}",
]


def leaves(items):
    for item in items:
        if "item" in item:
            yield from leaves(item["item"])
        else:
            yield item


def strip_ids(node):
    if isinstance(node, dict):
        node.pop("id", None)
        node.pop("_postman_id", None)
        for value in node.values():
            strip_ids(value)
    elif isinstance(node, list):
        for value in node:
            strip_ids(value)


def main(source: str, target: str) -> None:
    converted = json.load(open(source, encoding="utf-8"))

    folders: dict[str, list] = {}
    top_level = []
    for request_item in leaves(converted["item"]):
        request = request_item["request"]
        path = request["url"]["path"]
        request.pop("auth", None)  # inherit the collection's Bearer auth

        if path == ["auth", "login"]:
            request["auth"] = {"type": "noauth"}
            request["body"]["raw"] = json.dumps({"email": "{{email}}", "password": "{{password}}"}, indent=2)
            request_item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": LOGIN_TEST}}]

        segment = path[0] if path and path[0] else ""
        (folders.setdefault(segment, []) if segment else top_level).append(request_item)

    collection = {
        "info": {
            "name": "SDG Tag Heroes API",
            "description": DESCRIPTION,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [{"name": name, "item": items} for name, items in folders.items()] + top_level,
        "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{bearerToken}}", "type": "string"}]},
        "variable": VARIABLES,
    }
    strip_ids(collection)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{sum(len(items) for items in folders.values()) + len(top_level)} requests in {len(folders)} folders "
          f"written to {target}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
