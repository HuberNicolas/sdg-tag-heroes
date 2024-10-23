#!/bin/bash

echo "Starting Prefect server..."

# Start Prefect server on all interfaces, binding to port 4000
prefect server start --host 0.0.0.0 --port 4000
