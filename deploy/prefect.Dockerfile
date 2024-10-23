FROM prefecthq/prefect:2-latest

COPY deploy/entrypoint.prefect.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint script
ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]
