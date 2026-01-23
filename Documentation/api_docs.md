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
      { 
        "name": "Project A", 
        "requirements": "Requirement text...", 
        "project_focus": "Focus areas...",
        "created_at": "2026-01-20T22:54:02" 
      }
    ]
    ```

### Create or Update Project
*   **Endpoint**: `POST /api/projects`
*   **Request Body**:
    ```json
    {
      "name": "Project Name",
      "requirements": "Mandatory requirements text",
      "project_focus": "Optional focus areas for prompts"
    }
    ```
*   **Response**: `200 OK`
    ```json
    { "id": 1, "name": "Project Name", "message": "Project created/updated" }
    ```

### Update Project Details
*   **Endpoint**: `PATCH /api/projects/{name}`
*   **Description**: Partially update project requirements or focus.
*   **Request Body**:
    ```json
    {
      "requirements": "New requirements text (optional)",
      "project_focus": "New focus text (optional)"
    }
    ```
*   **Response**: `200 OK`

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
      { "name": "Production", "created_at": "2026-01-20T22:54:02" },
      { "name": "Staging", "created_at": "2026-01-20T22:54:02" }
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
      "requirement_analysis": "STATUS: PASSED\nSUMMARY: Brief summary...\nWORKFLOW: 1. Step one\n2. Step two...",
      "similar_prompts": [
        { "id": 101, "prompt_text": "Existing prompt...", "similarity": 0.92, "created_at": "2026-01-20T22:54:02" }
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

### Get System Info
*   **Endpoint**: `GET /api/info`
*   **Description**: Returns current application version and status.
*   **Response**: `200 OK`
    ```json
    { "version": "0.6.1", "status": "healthy", "name": "Prompt Similarity Detector" }
    ```
