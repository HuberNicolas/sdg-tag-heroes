## Tailwind issues from building
## Adding all tailwind dependencies (forms, aspect-ration), manually, make sure that those are
## NOT dev dependency.

# Use Node 16 Alpine image as the build image
FROM node:20-alpine AS builder

# Create work directory in app folder
WORKDIR /app

# Install required packages for Node image
RUN apk --no-cache add openssh g++ make python3 git

# Install pnpm globally
RUN npm install -g pnpm

# Copy over package.json and pnpm-lock.yaml files
COPY frontend/package.json /app/
COPY frontend/pnpm-lock.yaml /app/

# Install all dependencies using pnpm
RUN pnpm install --frozen-lockfile

# Copy over all files to the work directory
ADD frontend /app

# Build the project
RUN pnpm run build

# Start final image
FROM node:16-alpine

WORKDIR /app

# Copy over build files from the builder step
COPY --from=builder /app/.output /app/.output
COPY --from=builder /app/.nuxt /app/.nuxt

# Expose the host and port 3000 to the server
ENV HOST 0.0.0.0
EXPOSE 3000

# Run the built project with Node
ENTRYPOINT ["node", ".output/server/index.mjs"]
