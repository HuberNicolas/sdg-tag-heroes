FROM ubuntu:latest

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


#RUN wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2404-arm64-100.10.0.deb && \
#    dpkg -i mongodb-database-tools-ubuntu2404-arm64-100.10.0.deb && \
#    rm mongodb-database-tools-ubuntu2404-arm64-100.10.0.deb && \
#    apt-get clean && rm -rf /var/lib/apt/lists/*


# Install MongoDB Database Tools for AMD64
RUN wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2404-x86_64-100.10.0.deb && \
    dpkg -i mongodb-database-tools-ubuntu2404-x86_64-100.10.0.deb && \
    rm mongodb-database-tools-ubuntu2404-x86_64-100.10.0.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
