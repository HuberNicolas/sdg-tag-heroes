FROM debian:latest

# Install essential tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    net-tools \
    iputils-ping \
    mariadb-client \
    nano \
    vim \
    && apt-get clean

