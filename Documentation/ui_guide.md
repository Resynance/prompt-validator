# Prompt Manager Web Interface Guide

This guide provides an overview of the features and workflows available in the Prompt Manager web interface.

## 1. Sidebar Navigation

The sidebar is your primary navigation hub, allowing you to switch between the three main views:
*   **🔍 Prompt Checker**: The core workspace for analyzing and saving prompts.
*   **⚙️ Project & Environment Management**: Manage your organizational structure (Projects and Environments).
*   **🛠️ Settings**: Configure global application parameters and perform system maintenance.

Recent projects are also listed in the sidebar for quick reference.

---

## 2. Prompt Checker View

This is where you'll spend most of your time analyzing prompts.

### Scope Selection
*   **Header Dropdowns**: Use the interactive dropdowns in the top header to select your **Project** and **Environment**. 
*   **Dynamic Loading**: Selecting a project will automatically populate the associated environments.

### Analysis Workflow
1.  **Input**: Enter your prompt text into the central editor.
2.  **Analyze**: Click **"Analyze Prompt"** to trigger the background processing.
3.  **Review Results**:
    *   **Compliance Analysis**: View LLM-generated feedback on how well your prompt aligns with the project's defined requirements.
    *   **Similarity Matches**: See existing prompts that are similar to your input. **Creation timestamps** are displayed alongside each match to provide historical context.
    *   **Intelligent Auto-Save**: If no similar prompts are found, the system saves your prompt automatically. If matches exist, you can choose to **"Save to Database"** manually.

---

## 3. Project & Environment Management

Manage the hierarchy of your prompt library.

### Projects
*   **Add Project**: Create a new project container.
*   **Edit Requirements**: Update the compliance criteria for a project.
*   **Creation History**: View the exact date each project was initialized.
*   **PDF Import**: In the project modal, use the **"Import PDF"** button to automatically extract requirements from a PDF document.
*   **Delete**: Remove a project and all its nested data.

### Environments
*   **Manage Envs**: Click **"Envs"** next to a project to see its specific environments and their **creation dates**.
*   **Clear Prompts**: Delete all saved prompts within a specific environment while keeping the environment configuration intact.
*   **Delete Env**: Remove an environment entirely.

---

## 4. Settings View

Configure application-wide settings.

### Provider Configuration
*   **LM Studio URL**: Set the base URL for your local LM Studio server. This setting is **automatically persisted** in your browser, so you don't need to re-enter it on every visit.

### Technical Troubleshooting
*   **Reset Prompt Database**: If you encounter a "Dimension Mismatch" error (common when switching embedding models in LM Studio), click this button. It will reformat the database schema to match your current model.
    > [!CAUTION]
    > This action is destructive and will delete all saved prompts.

---

---

## 5. Model Selection & Performance

The quality of your analysis depends heavily on the models loaded in LM Studio.

### Recommended Models
*   **Chat Model**: `Llama-3-8B-Instruct` is highly recommended for compliance analysis. 
    *   **Settings**: In LM Studio, set your **Context Length (n_ctx)** to at least `8192` to handle longer requirement documents.
*   **Embedding Model**: `nomic-embed-text` is a reliable and fast choice for generating prompt vectors.

### Performance Tips
*   Ensure your LM Studio server is running before clicking **Analyze Prompt**.
*   If analysis is slow, check your hardware utilization in your OS Activity Monitor.

## 6. UI Features
*   **Glassmorphism Theme**: A premium dark theme with blur effects and sleek animations.
*   **Responsive State**: Sidebar selection and header dropdowns are always synchronized.
*   **Detailed Feedback**: Tooltips and clear status badges (Success, Warning, Error) guide you through the analysis process.
