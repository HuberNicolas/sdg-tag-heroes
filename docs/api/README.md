# API

The SDG Tag Heroes API is a [FastAPI](https://fastapi.tiangolo.com/) application in [`api/`](../../api). It runs in the
`api` container on <http://localhost:1002> (see the [main README](../../README.md#getting-started) for how to start it).

There are two ways to explore it:

- **Swagger UI** at <http://localhost:1002/docs> (or ReDoc at <http://localhost:1002/redoc>), generated from the code and
  always up to date
- **Postman**, with the collection in this folder

## Postman collection

[`sdg-tag-heroes.postman_collection.json`](sdg-tag-heroes.postman_collection.json) contains all 111 requests of the
API, grouped into folders by the first part of the URL path. It is generated from the API's `openapi.json` (see
[Updating the collection](#updating-the-collection)). Each request has example bodies and example responses with
placeholder values.

### Import

1. In Postman, choose **Import** and select `docs/api/sdg-tag-heroes.postman_collection.json`.
2. Open the collection, go to **Variables**, and set `password` for the account in `email`.
3. Send **auth → Login**. The request stores the returned JWT in `bearerToken`.
4. Every other request uses `bearerToken` automatically (collection-level Bearer auth).

Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (in `env/backend.env`). Send the login request again to get a new one.

### Variables

| Variable      | Default                 | Meaning                                                  |
|---------------|-------------------------|----------------------------------------------------------|
| `baseUrl`     | `http://localhost:1002` | Where the API runs                                       |
| `email`       | `labeler@tagheroes.ch`  | Account used by the login request (from `env/users.env`) |
| `password`    | *(empty)*               | Password of that account                                 |
| `bearerToken` | *(empty)*               | Set by the login request                                 |

Path parameters (for example `:publication_id` or `:sdg`) are set in the **Params** tab of each request.

> [!IMPORTANT]
> Do not commit the collection with a filled-in `password` or `bearerToken`. Postman stores the current values of
> collection variables in the export.

### Updating the collection

After changing the API, regenerate the collection from the OpenAPI schema of the running API, from the repository
root:

```bash
curl -s http://localhost:1002/openapi.json -o openapi.json
```

```bash
npx openapi-to-postmanv2@4 -s openapi.json -o converted.json -p -O folderStrategy=Paths
```

```bash
python3 docs/api/finalize_postman_collection.py converted.json docs/api/sdg-tag-heroes.postman_collection.json
```

The first command is Postman's own converter (the same one the Postman import uses).
[`finalize_postman_collection.py`](finalize_postman_collection.py) groups the requests into one folder per resource,
sets the collection's Bearer auth and variables, and adds the login test script. Delete `openapi.json` and
`converted.json` afterwards.

## Authentication

`POST /auth/login` takes JSON (`{"email": "…", "password": "…"}`) and returns `{"access_token": "…", "token_type":
"bearer"}`. Send the token as `Authorization: Bearer <token>`. `GET /auth/protected` checks whether a token is valid.

Users, roles, and passwords come from `env/users.env` or the user loader (see
[Building the dataset](../../README.md#3-users)).

## Endpoint groups

| Prefix                       | Resource                                                                  |
|------------------------------|---------------------------------------------------------------------------|
| `/auth`                      | Login and token check                                                     |
| `/users`                     | Users, own profile, filtering by role                                     |
| `/users-profiles`            | GPT suggestions: which SDG fits a user's skills or interests              |
| `/publications`              | Publications, filtering, similarity search, GPT summaries/keywords/facts   |
| `/authors`                   | Authors                                                                   |
| `/sdgs`                      | SDG goals and targets                                                     |
| `/sdg-predictions`           | Model predictions per publication                                         |
| `/explanations`              | Token-level SDG explanations (MongoDB)                                    |
| `/dimensionality-reductions` | UMAP coordinates for the exploration maps                                 |
| `/collections`               | Topic collections                                                         |
| `/user-labels`               | Votes and comments players give on a publication                          |
| `/votes`                     | Up/down votes on user labels                                              |
| `/annotations`               | Annotations on publications                                               |
| `/label-summaries`           | Aggregated labels per publication                                         |
| `/label-histories`           | History of label changes                                                  |
| `/label-decisions`           | Scenarios and final label decisions                                       |
| `/banks`                     | XP per SDG and its history                                                |
| `/wallets`                   | Coins per SDG and its history                                             |
| `/ranks`                     | SDG ranks of users                                                        |

The route handlers are in [`api/app/routes/`](../../api/app/routes), the response schemas in
[`schemas/`](../../schemas), and the request bodies in [`request_models/`](../../request_models).
