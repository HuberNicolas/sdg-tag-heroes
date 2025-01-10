FROM ubuntu:latest

# Install essential tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    net-tools \
    iputils-ping \
    mariadb-client \
    unzip \
    nano \
    vim \
    gnupg \
    && apt-get clean


#RUN wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2404-arm64-100.10.0.deb && \
#    dpkg -i mongodb-database-tools-ubuntu2404-arm64-100.10.0.deb && \
#    rm mongodb-database-tools-ubuntu2404-arm64-100.10.0.deb && \
#    apt-get clean && rm -rf /var/lib/apt/lists/*


# Install MongoDB Database Tools for AMD64
RUN wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2404-x86_64-100.10.0.deb && \
    dpkg -i mongodb-database-tools-ubuntu2404-x86_64-100.10.0.deb && \
    rm mongodb-database-tools-ubuntu2404-x86_64-100.10.0.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Add MongoDB APT repository and install MongoDB client (mongosh)
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && apt-get install -y mongodb-org-shell && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
