# Production image of the frontend: builds the Nuxt app and serves it with the Nitro server.
#   docker build -f deploy/frontend.prod.Dockerfile -t sdg-tag-heroes-frontend-prod .
#   docker run -p 3000:3000 -e NUXT_PUBLIC_API_URL=http://localhost:1002 sdg-tag-heroes-frontend-prod
# The API address is read at runtime from NUXT_PUBLIC_API_URL (the browser calls the API directly).

FROM node:20-alpine AS builder

WORKDIR /app

# Native build tools for dependencies that compile on install
RUN apk --no-cache add g++ make python3 git

# Install exactly the locked versions; newer packages break the layout (see TODO.md)
COPY frontend/package.json frontend/package-lock.json /app/
RUN npm ci

COPY frontend /app
# The default Node heap is too small for the build (Plotly, D3)
RUN NODE_OPTIONS=--max-old-space-size=4096 npm run build

FROM node:20-alpine

WORKDIR /app

# .output contains the server and everything it needs, including its own node_modules
COPY --from=builder /app/.output /app/.output

ENV HOST=0.0.0.0 \
    PORT=3000 \
    NODE_ENV=production
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
