# Prompt Similarity Detector
Developed by **Max Turner** ([Resynance](https://github.com/Resynance))

A modern, hierarchical tool for managing LLM prompts with intelligent similarity detection and compliance checking. Built with FastAPI, PostgreSQL (`pgvector`), and LM Studio.

## Key Features

- **Hierarchical Management**: Organize prompts under **Projects** and **Environments**.
- **Interactive Header Navigation**: Quickly switch between projects and environments directly in the header.
- **Intelligent Check & Auto-Save**: Analyze prompts for compliance and similarity; unique prompts are automatically saved to the database.
- **Dedicated Settings View**: Centralized management for LM Studio URLs and technical troubleshooting (Database Reset).
- **Persistent Configuration**: LM Studio URL is remembered across sessions using local storage.
- **PDF Requirement Import**: Extract project requirements directly from PDF documents.
- **Historical Tracking**: Every project, environment, and prompt is timestamped, providing a full audit trail of your prompt library's evolution.
- **Dark Mode UI**: A premium, glassmorphism-inspired dark theme.

## Prerequisites

1.  **LM Studio**:
    *   Load an embedding model (`Llama-3-8B-Instruct` recommended) and a chat model (e.g., `Llama-3-8B-Instruct`).
    *   Start the **Local Server** (default: `http://localhost:1234/v1`).
2.  **PostgreSQL**:
    *   Ensure PostgreSQL is running with the `pgvector` extension installed.
    *   See the [PostgreSQL & pgvector Setup Guide](Documentation/postgres_setup.md) for detailed installation and user configuration steps.
    *   The app will automatically manage the `prompt_similarity` database schema.

## Setup

1.  **Environment**:
    ```bash
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Start the Server**:
    ```bash
    python3 app.py
    ```
3.  **Access the App**: Open [http://localhost:8000](http://localhost:8000)

## Deployment Options

### Standard (Local)
Follow the [Setup](#setup) instructions above to run directly on your host machine.

### Docker (Recommended for Portability)
Deploy the entire stack (App + DB) with a single command:
```bash
docker-compose up --build
```
See the [Docker Setup Guide](Documentation/docker_setup.md) for detailed configuration.

## How It Works

1.  **Compliance Analysis**: Compares your input prompt against project-level requirements using LLM reasoning.
2.  **Embedding Generation**: Creates a high-dimensional vector of your prompt using LM Studio.
3.  **Similarity Search**: Uses `pgvector` to find existing prompts with high cosine similarity in the selected environment.
4.  **Auto-Persistence**: If no similarities are found, the prompt is saved immediately. If matches exist, you have the option to "Save anyway".

## Testing

The project includes an automated test suite covering both the database layer and the API.

1.  **Prep Test Database**:
    ```bash
    psql -U promptmanager -d postgres -c "CREATE DATABASE prompt_similarity_test OWNER promptmanager;"
    psql -U promptmanager -d prompt_similarity_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
    ```
2.  **Run Tests**:
    ```bash
    source venv/bin/activate
    export PYTHONPATH=$PYTHONPATH:.
    pytest tests/
    ```

## Technical Troubleshooting

If you switch embedding models in LM Studio (e.g., from 1536-dim to 768-dim), navigate to the **Settings** page and click **"Reset Prompt Database"**. This will re-initialize the database schema to match your current model's dimensions.

## Developer Resources

- [Web Interface User Guide](Documentation/ui_guide.md): Visual and functional walkthrough of the UI.
- [PostgreSQL & pgvector Setup](Documentation/postgres_setup.md): Installation guide for Windows and macOS.
- [Docker Setup Guide](Documentation/docker_setup.md): Containerized deployment instructions.
- [System Architecture & Tech Stack](Documentation/architecture.md): Technical diagrams and component breakdowns.
- [AWS & Multi-User Roadmap](Documentation/aws_and_multiuser_roadmap.md): Strategy for scaling to the cloud and multiple tenants.
- [Testing Guide](Documentation/testing_guide.md): Details on the automated test suite and how to run it.
- [REST API Documentation](Documentation/api_docs.md): Technical details for programmatic interaction.
