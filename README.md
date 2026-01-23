# Prompt Similarity Detector
Developed by **Max Turner** ([Resynance](https://github.com/Resynance))

A modern, hierarchical tool for managing LLM prompts with intelligent similarity detection and compliance checking. Built with FastAPI, PostgreSQL (`pgvector`), and LM Studio.

## Key Features

- **Hierarchical Management**: Organize prompts under **Projects** and **Environments**.
- **Project Focus**: Define optional focus areas (e.g., "Performance", "Clean Code") for more granular compliance checking.
- **Mandatory Requirements**: Every project requires defined requirements to ensure consistent compliance analysis.
- **Interactive Header Navigation**: Quickly switch between projects and environments directly in the header.
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

1.  **Compliance Analysis**: Compares your input prompt against **Core Requirements** and specific **Project Focus** areas using LLM reasoning. Satisfactory prompts receive descriptive positive feedback.
2.  **Embedding Generation**: Creates a high-dimensional vector of your prompt using LM Studio.
3.  **Similarity Search**: Uses `pgvector` to find existing prompts with high cosine similarity in the selected environment.
4.  **Auto-Persistence**: If no similarities are found, the prompt is saved immediately. If matches exist, you have the option to "Save anyway".
5.  **Button Protection**: The interface prevents duplicate submissions by disabling the action button during active analysis.

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
    
## Release & Packaging

To package the application for release, use the provided script:
```bash
./scripts/package.sh
```
This will create a versioned `.tgz` file (e.g., `prompt-manager-v0.6.2.tgz`) containing only the necessary source code and documentation, excluding developer environments and history.

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
- [Release Notes](Documentation/release-notes.md): Chronological record of features and fixes.
