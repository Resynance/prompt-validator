# Docker Deployment Guide

The Prompt Similarity Detector can be deployed as a self-contained suite using Docker and Docker Compose. This setup includes the FastAPI application and a PostgreSQL database pre-configured with the `pgvector` extension.

## 1. Prerequisites

*   **Docker Desktop**: Installed and running on your system ([Download Here](https://www.docker.com/products/docker-desktop/)).
*   **LM Studio**: Running on your host machine with an embedding and chat model loaded.

## 2. Fast Track (Quick Start)

Navigate to the project root and run:

```bash
docker-compose up --build
```

The application will be accessible at [http://localhost:8000](http://localhost:8000).

---

## 3. Configuration

The orchestration is managed via `docker-compose.yml`. You can customize the behavior using environment variables.

### Key Environment Variables

| Variable | Description | Default in Compose |
| :--- | :--- | :--- |
| `DB_HOST` | Database host name | `db` |
| `DB_NAME` | Database name | `prompt_similarity` |
| `DB_USER` | Database user | `promptmanager` |
| `DB_PASSWORD` | Database password | `password` |
| `LM_STUDIO_URL` | URL to host's LM Studio | `http://host.docker.internal:1234/v1` |

### Accessing LM Studio from Docker

Since LM Studio runs on your host machine and the app runs inside a container, the app needs to reach the "outside" world.
*   **macOS/Windows**: Use `http://host.docker.internal:1234/v1`.
*   **Linux**: You may need to use your machine's local IP address or configure `extra_hosts` in the compose file.

---

## 4. Manual Builds

If you wish to build the application container separately:

```bash
docker build -t prompt-manager-app .
```

To run it independently (requires an external Postgres with pgvector):

```bash
docker run -p 8000:8000 -e DB_HOST=your_db_host prompt-manager-app
```

## 5. Persistence

The PostgreSQL data is persisted using a Docker volume named `postgres_data`. This ensures your projects, environments, and prompts are saved even if the containers are stopped or removed.

To completely wipe the database and start fresh:

```bash
docker-compose down -v
```
