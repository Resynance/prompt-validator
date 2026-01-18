# Prompt Similarity Detector

This tool uses LM Studio and PostgreSQL with `pgvector` to identify similar or duplicate QA prompts.

## Prerequisites

1.  **LM Studio**:
    *   Open LM Studio.
    *   Load an embedding model (e.g., `text-embedding-nomic-embed-text-v1.5` or similar).
    *   Start the **Local Server** (usually on port 1234).
2.  **PostgreSQL**:
    *   Ensure PostgreSQL is running.
    *   The tool creates a database named `prompt_similarity` and a table `prompts`.
    *   The `pgvector` extension must be installed.

## Setup

1.  Navigate to the project directory:
    ```bash
    cd "Prompt Similarity Detector"
    ```
2.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```

## Usage

Run the `similarity_check.py` script with the project name and the prompt you want to check. 

> [!TIP]
> If you get a connection error, LM Studio might be on a different port. Use the `--url` flag to specify it (e.g., if LM Studio is on port 41343).

```bash
python similarity_check.py --project "MyProject" --prompt "This is a test prompt." --url http://localhost:41343/v1
```

### Options

*   `--project`: The name of the project (required).
*   `--prompt`: The prompt text to check (required).
*   `--url`: The base URL for LM Studio API (default: `http://localhost:1234/v1`).
*   `--threshold`: The similarity threshold (0.0 to 1.0, default: 0.85).

## How it works

1.  Generates an embedding for the input prompt using LM Studio's `/embeddings` endpoint.
2.  Queries the PostgreSQL database for existing prompts in the same project.
3.  Calculates cosine similarity using `pgvector`.
4.  If similar prompts are found, it lists them and asks for confirmation before saving.
5.  If no similar prompts are found (or if you confirm), it saves the new prompt to the database.
