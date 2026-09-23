# API

The SDG Tag Heroes API is a [FastAPI](https://fastapi.tiangolo.com/) application in [`api/`](../../api). It runs in the
`api` container on <http://localhost:1002> (see the [main README](../../README.md#getting-started) for how to start it).

There are two ways to explore it:

- **Swagger UI** at <http://localhost:1002/docs> (or ReDoc at <http://localhost:1002/redoc>), generated from the code and
  always up to date
- **Postman**, with the collection in this folder

## Postman collection

[`sdg-tag-heroes.postman_collection.json`](sdg-tag-heroes.postman_collection.json) contains 96 requests, grouped into
folders by URL path. Each request has example bodies and example responses (200, 401, 403, 404, 422) with placeholder
values.

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

### Endpoints not yet in the collection

These routes exist in the code but were added after the collection was exported. They are available in Swagger UI:

| Method | Path                                                             |
|--------|------------------------------------------------------------------|
| GET    | `/banks/latest`                                                  |
| GET    | `/label-decisions/users/{user_id}`                               |
| GET    | `/label-decisions/{reduction_shorthand}/scenarios/{scenario_type}` |
| GET    | `/user-labels/users/{user_id}`                                   |
| GET    | `/publications/scenarios/{scenario_type}/{top_k}`                |
| GET    | `/publications/users/{user_id}/labeled`                          |
| GET    | `/{resource}/global/scenarios/least-labeled/{top_k}` for `publications`, `label-decisions`, `sdg-predictions`, `dimensionality-reductions` |
| GET    | `/{resource}/global/scenarios/max-entropy/{top_k}` for the same four resources |

### Updating the collection

The collection was created by importing the OpenAPI schema of the running API. To regenerate it with all current
endpoints:

1. Start the API.
2. In Postman, choose **Import** and enter `http://localhost:1002/openapi.json`.
3. Set the new collection's auth to Bearer `{{bearerToken}}`, add the variables above, and copy the test script of the
   login request:

   ```js
   if (pm.response.code === 200) {
     pm.collectionVariables.set("bearerToken", pm.response.json().access_token);
   }
   ```

4. Export it as **Collection v2.1**, replace the file in this folder, and check that it contains no password or token.

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
