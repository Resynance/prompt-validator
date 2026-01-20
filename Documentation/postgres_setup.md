# PostgreSQL & pgvector Setup Guide

This guide details how to install and configure PostgreSQL with the `pgvector` extension for use with the Prompt Similarity Detector on macOS and Windows.

## 1. macOS Setup (Recommended: Homebrew)

The easiest way to install PostgreSQL on macOS is via [Homebrew](https://brew.sh/).

1.  **Install PostgreSQL**:
    ```bash
    brew install postgresql@14
    brew tap pgvector/pgvector
    brew install pgvector
    ```
2.  **Start the Service**:
    ```bash
    brew services start postgresql@14
    ```

---

## 2. Windows Setup

1.  **Download & Install PostgreSQL**:
    *   Download the installer from [EnterpriseDB (EDB)](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
    *   Follow the installation wizard (PostgreSQL 14 or 15 recommended).
2.  **Install `pgvector`**:
    *   The easiest way on Windows is to download a pre-compiled binary.
    *   Visit the [pgvector releases page](https://github.com/pgvector/pgvector/releases).
    *   Download the Windows zip for your Postgres version.
    *   Copy the contents (`vector.dll`, `vector.control`, etc.) into your PostgreSQL `lib` and `share/extension` directories (usually in `C:\Program Files\PostgreSQL\{version}\`).
3.  **Alternative (Stack Builder)**:
    *   Run **Stack Builder** (included with the installer).
    *   Look for "Add-ons" or "Spatial Extensions" to see if `pgvector` is listed for easy installation.

---

## 3. Database & Extension Initialization

Once PostgreSQL is installed and running, you need to enable the `pgvector` extension.

1.  **Connect to Postgres** (via terminal or tool like pgAdmin):
    ```bash
    psql -U postgres
    ```
2.  **Create the Database**:
    ```sql
    CREATE DATABASE prompt_similarity;
    \c prompt_similarity;
    ```
3.  **Enable pgvector**:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

---

## 4. Connection Configuration

By default, the application connects to PostgreSQL using the following parameters:
*   **Host**: `localhost`
*   **Port**: `5432`
*   **Database**: `prompt_similarity`
*   **User**: `postgres`

> [!NOTE]
> If you have a password set for your `postgres` user, ensure your environment is configured to handle the connection (e.g., via a `.env` file or system environment variables).

## 5. Model Compatibility

If you switch between different embedding models (e.g., changing from a 768-dimension model to a 1024-dimension model), you must reset your `prompts` table to match the new dimensions. 

You can do this safely through the **Settings** page in the web interface by clicking **"Reset Prompt Database"**.
