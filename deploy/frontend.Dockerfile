# Use Node 20 Alpine image for both build and dev server
FROM node:20-alpine AS dev

# Create work directory in app folder and give deployer user ownership
WORKDIR /app

# Install required packages for Node image
RUN apk --no-cache add openssh g++ make python3 git

# Install pnpm globally
# RUN npm install -g pnpm

# Copy over package.json
COPY frontend/package.json /app/

# Update npm
RUN npm install -g npm@11.1.0

# Install all dependencies (dev and prod) using npm
RUN npm install

# Expose the host and port for the dev server
ENV HOST 0.0.0.0
EXPOSE 3000

# Run the development server as non-root user
CMD ["npm", "run", "dev"]
