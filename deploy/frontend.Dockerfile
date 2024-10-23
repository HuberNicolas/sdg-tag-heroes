# Use Node 20 Alpine image for both build and dev server
FROM node:20-alpine AS dev

# Create a non-root user with the same UID/GID as your deployer user on the host
# deployer@herold:~$ id -u deployer -> 1112
RUN addgroup -g 1112 deployer && adduser -D -u 1112 -G deployer deployer

# Create work directory in app folder and give deployer user ownership
WORKDIR /app
RUN chown -R deployer:deployer /app

# Install required packages for Node image
RUN apk --no-cache add openssh g++ make python3 git

# Install pnpm globally
RUN npm install -g pnpm

# Switch to deployer user
USER deployer

# Copy over package.json and pnpm-lock.yaml files
COPY --chown=deployer:deployer frontend/package.json /app/
COPY --chown=deployer:deployer frontend/pnpm-lock.yaml /app/

# Install all dependencies (dev and prod) using pnpm
RUN pnpm install

# Expose the host and port for the dev server
ENV HOST 0.0.0.0
EXPOSE 3000

# Run the development server as non-root user
CMD ["pnpm", "dev"]
