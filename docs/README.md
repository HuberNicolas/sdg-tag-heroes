# Documentation

Start with the [main README](../README.md): it explains what SDG Tag Heroes is and how to run it. These guides go
into detail.

## Understand

| Guide                               | Content                                                                    |
|-------------------------------------|----------------------------------------------------------------------------|
| [Architecture](architecture.md)     | Code layers of the backend and the frontend, how a request is handled, models vs. schemas |
| [API](api/README.md)                | Authentication, endpoint groups, Postman collection                         |

## Set up and run

| Guide                               | Content                                                                    |
|-------------------------------------|----------------------------------------------------------------------------|
| [Docker](docker.md)                 | Services, ports, volumes, common commands, freeing disk space              |
| [Building the dataset](dataset.md)  | Every dataset script, in order: schema, publications, predictions, maps, topics, labels, explanations, fixtures |
| [Databases](databases.md)           | Database UIs, backup and restore of MariaDB, MongoDB and Qdrant            |
| [Deployment](deployment.md)         | Running the stack on a server, restoring backups there, reaching the admin UIs |

## Develop

| Guide                                   | Content                                                                |
|-----------------------------------------|------------------------------------------------------------------------|
| [Development](development.md)           | Python environment, linting and formatting, conventions, where to change what |
| [Migrations](migrations.md)             | Changing the database schema with Alembic                              |
| [Frontend](../frontend/README.md)       | Frontend setup, pages, structure, production build                     |
| [Troubleshooting](troubleshooting.md)   | Known errors and their fixes                                           |
