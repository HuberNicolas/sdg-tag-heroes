# Troubleshooting

Errors that came up while developing and running SDG Tag Heroes, and how to fix them.

## Docker

### A database stops with "No space left on device"

Docker's virtual machine is full. The database containers then crash, for example MariaDB with
`Errcode: 28 "No space left on device"`. Free space as described in [Docker](docker.md#cleaning-up), or give Docker
Desktop more disk space.

### The API cannot connect to a database

Check that the database container runs (`docker compose ps`) and that `env/<database>.env` has the right credentials.
The API logs the result of each connection check at startup (`docker compose logs api`).

## Frontend

### `listen EADDRINUSE: address already in use /tmp/nitro/worker-….sock`

The Nuxt dev server in the container was not shut down cleanly. Rebuild the container:

```bash
docker compose up -d --build frontend
```

### Tailwind or PostCSS errors after running the frontend both locally and in Docker

Nuxt's build folder `.nuxt/` contains absolute paths. The `frontend` container keeps its own `.nuxt/` in an
anonymous volume. If the error persists, recreate the container with fresh volumes:

```bash
docker compose up -d --build --force-recreate -V frontend
```

### The layout is broken after updating packages

Newer versions of Nuxt (3.21) and Nuxt UI (2.22) break the layout. Install exactly the locked versions with `npm ci`
and do not upgrade the frontend packages without checking every page.

### The overview map is empty

The overview map is split into `NUXT_PUBLIC_MAP_PARTITIONS` parts (default 1000), one per universe. A small dataset
has fewer parts; set `NUXT_PUBLIC_MAP_PARTITIONS=3` in `frontend/.env` for the dummy dataset.

## API

### Every request returns 401

The token expired (after `ACCESS_TOKEN_EXPIRE_MINUTES`, see `env/backend.env`) or was signed with another
`SECRET_KEY`. Log in again.

### Maps or levels are empty

The API shows the predictions of `PREDICTION_MODEL` (default `Aurora`). With the dummy dataset, start the API with
`PREDICTION_MODEL=Dvdblk`. After new UMAP models were written, restart the API: `docker compose restart api`.

## Deployment

### phpMyAdmin shows `Uncaught SyntaxError: Unexpected token '<'`

The web server returns HTML instead of the PHP application's JavaScript, typically behind a reverse proxy that does
not pass PHP requests through. Check that the proxy forwards the phpMyAdmin path unchanged, and in an Apache setup
that PHP files are handled:

```apache
<Directory /path/to/phpmyadmin>
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>

AddType application/x-httpd-php .php
```
