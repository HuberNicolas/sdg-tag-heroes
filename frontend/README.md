# SDG Tag Heroes – Frontend

The game's web interface: a single-page application built with [Nuxt 3](https://nuxt.com/) and Vue 3. It talks to the
[API](../docs/api/README.md) and keeps the loaded data in [Pinia](https://pinia.vuejs.org/) stores.

| | |
|---|---|
| **Framework** | Nuxt 3 (client-side rendering, `ssr: false`), Vue 3, TypeScript |
| **UI** | [Nuxt UI 2](https://ui.nuxt.com/) with Tailwind CSS 3, [daisyUI 4](https://daisyui.com/), [Material Design Icons](https://icones.js.org/collection/mdi) |
| **Visualisations** | [D3](https://d3js.org/), [Plotly](https://plotly.com/javascript/), [leader-line](https://github.com/anseki/leader-line) |
| **State** | Pinia stores, [VueUse](https://vueuse.org/) |
| **Screens** | Laptop to ultrawide (1280–3440 px) |

## Getting started

Requires [Node.js](https://nodejs.org/) 20 or newer and a running API (see the [main README](../README.md#quick-start)).

```bash
cp .env.example .env
```

```bash
npm ci
```

```bash
npm run dev
```

Open <http://localhost:3000> and log in with an account from `env/users.env`. `npm ci` installs exactly the versions
in `package-lock.json`.

> [!WARNING]
> Do not upgrade the packages without checking every page. Newer versions of Nuxt (3.21) and Nuxt UI (2.22) break the
> layout.

To run the frontend in Docker instead, with hot reload on port 3030, use `docker compose up -d --build frontend` from
the repository root.

## Configuration

| Variable                     | Default | Meaning                                                                         |
|------------------------------|---------|---------------------------------------------------------------------------------|
| `API_URL`                    | –       | Where the browser reaches the API, e.g. `http://localhost:1002`                 |
| `NUXT_PUBLIC_MAP_PARTITIONS` | `1000`  | Parts the overview map is split into, one per universe; `3` for the dummy dataset |

Both are read from `.env` in development. At runtime, [Nuxt's runtime config](https://nuxt.com/docs/guide/going-further/runtime-config)
reads `NUXT_PUBLIC_API_URL` and `NUXT_PUBLIC_MAP_PARTITIONS`.

## Commands

| Command            | What it does                                        |
|--------------------|-----------------------------------------------------|
| `npm run dev`      | Development server with hot reload on port 3000     |
| `npm run build`    | Production build into `.output/`                    |
| `npm run preview`  | Serves the production build locally                 |
| `npm run lint`     | ESLint (Nuxt config)                                |
| `npm run lint:fix` | ESLint with automatic fixes                         |
| `npm run format`   | Prettier                                            |

The build needs more memory than Node's default; if it fails with "JavaScript heap out of memory", run it with
`NODE_OPTIONS=--max-old-space-size=4096`.

## Pages

| Route                                  | Page                                                                          |
|----------------------------------------|-------------------------------------------------------------------------------|
| `/`, `/login`                          | Login                                                                         |
| `/profile`                             | The player's profile after login                                              |
| `/scenarios`                           | Choose a game mode: an SDG universe or a scenario (Confirm, Tiebreaker, …)    |
| `/exploration/publications/[level]`    | Overview map of all publications, split into universes                        |
| `/exploration/sdgs/[sdg]/[level]`      | Map of one SDG at one level, with quests and the publication table            |
| `/labeling/[publicationId]`            | Label a publication: vote, annotate, see explanations and other players' votes |
| `/users`, `/users/[id]`                | Players and their label decisions                                             |
| `/about`                               | How the game works                                                            |

Every page except the login requires a token. [`middleware/authentication.ts`](middleware/authentication.ts)
redirects to `/login` when the `access_token` cookie is missing.

## Structure

```
frontend/
├── pages/            # Routes (file-based routing)
├── layouts/          # default (navigation bar, full-height main area) and none (login)
├── components/       # Vue components; plots/ and quests/ group related ones
├── composables/      # use… API clients per resource, plots/ and glyph/ for D3 and Plotly drawings
├── stores/           # Pinia stores: loaded data and the player's selection
├── types/            # TypeScript interfaces of the API schemas
├── constants/        # SDG colours, icons and other constants
├── middleware/       # Route guard: redirects to /login without a token
├── utils/            # Small helpers: snake_case → camelCase, entropy, dates, avatars
├── assets/           # SDG glyph SVGs and the Tailwind entry file
└── public/           # Static files served as they are
```

Data flows from a page through a store to a composable, which calls the API; see
[Architecture](../docs/architecture.md#frontend). Visualisations redraw when their container changes size, with
[`useRedrawOnResize`](composables/useRedrawOnResize.ts).

## Production

[`deploy/frontend.prod.Dockerfile`](../deploy/frontend.prod.Dockerfile) builds the frontend and serves it with the
Nuxt server on port 3000. Run the commands from the repository root:

```bash
docker build -f deploy/frontend.prod.Dockerfile -t sdg-tag-heroes-frontend-prod .
```

```bash
docker run -p 3000:3000 -e NUXT_PUBLIC_API_URL=http://localhost:1002 sdg-tag-heroes-frontend-prod
```

The API address is set when the container starts, so one image works for every environment.
