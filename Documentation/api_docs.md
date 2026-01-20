# Prompt Manager REST API Documentation

This document details the REST API endpoints available in the Prompt Manager backend. The backend is built with FastAPI and is accessible at `http://localhost:8000`.

## Base URL
`http://localhost:8000`

---

## 1. Projects

### List All Projects
*   **Endpoint**: `GET /api/projects`
*   **Description**: Retrieves a list of all projects and their requirements.
*   **Response**: `200 OK`
    ```json
    [
      { "name": "Project A", "requirements": "Requirement text..." },
      { "name": "Project B", "requirements": "Requirement text..." }
    ]
    ```

### Create or Update Project
*   **Endpoint**: `POST /api/projects`
*   **Request Body**:
    ```json
    {
      "name": "Project Name",
      "requirements": "Optional requirements text"
    }
    ```
*   **Response**: `200 OK`
    ```json
    { "id": 1, "name": "Project Name", "message": "Project created/updated" }
    ```

### Delete Project
*   **Endpoint**: `DELETE /api/projects/{name}`
*   **Description**: Deletes a project and all its associated environments and prompts.
*   **Response**: `200 OK`
    ```json
    { "message": "Project 'Project Name' deleted" }
    ```

### Import Requirements from PDF
*   **Endpoint**: `POST /api/projects/import-pdf`
*   **Request Format**: `multipart/form-data`
*   **Body**: `file` (PDF file)
*   **Response**: `200 OK`
    ```json
    { "text": "Extracted text from PDF..." }
    ```

---

## 2. Environments

### List Environments for Project
*   **Endpoint**: `GET /api/projects/{project_name}/environments`
*   **Response**: `200 OK`
    ```json
    [
      { "name": "Production" },
      { "name": "Staging" }
    ]
    ```

### Create Environment
*   **Endpoint**: `POST /api/environments`
*   **Request Body**:
    ```json
    {
      "project_name": "Project A",
      "name": "Environment Name"
    }
    ```
*   **Response**: `200 OK`

### Delete Environment
*   **Endpoint**: `DELETE /api/projects/{project_name}/environments/{env_name}`
*   **Response**: `200 OK`

### Clear All Prompts in Environment
*   **Endpoint**: `DELETE /api/projects/{project_name}/environments/{env_name}/prompts`
*   **Description**: Deletes all saved prompts within a specific environment while keeping the environment itself.
*   **Response**: `200 OK`

---

## 3. Prompt Analysis & Persistence

### Check Prompt (Analyze)
*   **Endpoint**: `POST /api/check`
*   **Description**: Performs compliance analysis, generates embeddings, and checks for similarities.
*   **Request Body**:
    ```json
    {
      "project": "Project A",
      "environment": "Staging",
      "prompt": "The prompt text to check",
      "threshold": 0.85,
      "url": "http://localhost:1234/v1",
      "model": "optional-model-name"
    }
    ```
*   **Response**: `200 OK`
    ```json
    {
      "requirement_analysis": "Reasoning about compliance...",
      "similar_prompts": [
        { "id": 101, "prompt_text": "Existing prompt...", "similarity": 0.92 }
      ],
      "prompt_text": "The input prompt",
      "environment_id": 1,
      "was_saved": true
    }
    ```
    > [!NOTE]
    > `was_saved` will be `true` if no similar prompts were found and the prompt was automatically persisted.

### Manual Save Prompt
*   **Endpoint**: `POST /api/save`
*   **Description**: Manually persists a prompt into the database.
*   **Request Body**: (Same as `CheckRequest` used in `/api/check`)
*   **Response**: `200 OK`
    ```json
    { "message": "Prompt saved successfully" }
    ```

---

## 4. Debug & System

### Reset Prompt Database
*   **Endpoint**: `DELETE /api/debug/reset-prompts`
*   **Description**: Drops and recreates the `prompts` table to match the current model's embedding dimensions. **WARNING: Deletes all prompts.**
*   **Request Body**: (Requires a valid prompt/url to determine new dimensions)
*   **Response**: `200 OK`
    ```json
    { "message": "Prompt database reset to 768 dimensions" }
    ```
