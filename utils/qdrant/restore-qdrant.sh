#!/bin/env bash

# Check if the user provided a path as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/your/snapshot.file"
    exit 1
fi

# Get the .snapshot file path from the command-line argument
backup_path="$1"

# Check if the specified .snapshot file exists
if [ ! -f "$backup_path" ]; then
    echo "Specified .snapshot file not found: $backup_path"
    exit 1
else
    echo "Found .snapshot file: $backup_path"
fi

# Upload the backup
# or 'localhost:6333/collections/publications-mt/snapshots/upload'
upload_response=$(curl --location 'http://qdrant-database:6333/collections/publications-mt/snapshots/upload' \
--header 'Content-Type: multipart/form-data' \
--form "snapshot=@$backup_path")

# Check if the upload was successful
echo "$upload_response" | grep -q '"result":true'

if [ $? -eq 0 ]; then
    echo "Upload successful."
else
    echo "Upload failed. Backup was not restored."
fi
