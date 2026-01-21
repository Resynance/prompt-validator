// State Management
let projects = [];
let currentProject = null;
let currentEnv = null;
let currentView = 'checker';

// DOM Elements - Navigation
const navChecker = document.getElementById('nav-checker');
const navManage = document.getElementById('nav-manage');
const navSettings = document.getElementById('nav-settings');
const viewChecker = document.getElementById('view-checker');
const viewManage = document.getElementById('view-manage');
const viewSettings = document.getElementById('view-settings');

// DOM Elements - Checker
const projectList = document.getElementById('project-list');
const displayProject = document.getElementById('display-project');
const displayEnv = document.getElementById('display-env');
const promptEditor = document.getElementById('prompt-editor');
const runCheckBtn = document.getElementById('run-check');
const resultsArea = document.getElementById('results-area');
const lmStudioUrlInput = document.getElementById('lm-studio-url');

// DOM Elements - Management
const projectsListBody = document.getElementById('projects-list-body');
const envManageCard = document.getElementById('env-manage-card');
const envManageProjectName = document.getElementById('env-manage-project-name');
const envsListBody = document.getElementById('envs-list-body');
const manageAddProjectBtn = document.getElementById('manage-add-project');
const manageAddEnvBtn = document.getElementById('manage-add-env');

// DOM Elements - Modals
const projectModal = document.getElementById('project-modal');
const envModal = document.getElementById('env-modal');
const addProjectBtn = document.getElementById('add-project-btn');
const modalProjectName = document.getElementById('modal-project-name');
const modalProjectReqs = document.getElementById('modal-project-reqs');
const modalEnvName = document.getElementById('modal-env-name');
const saveProjectBtn = document.getElementById('save-project-btn');
const saveEnvBtn = document.getElementById('save-env-btn');

async function init() {
    // Load saved URL from local storage
    const savedUrl = localStorage.getItem('lm-studio-url');
    if (savedUrl) lmStudioUrlInput.value = savedUrl;

    setupEventListeners();
    await fetchProjects();
    if (projects.length > 0 && !currentProject) {
        await selectProject(projects[0]);
    }
    switchView('checker');
}

// --- Navigation ---
function switchView(viewName) {
    currentView = viewName;

    // Toggle views
    viewChecker.style.display = viewName === 'checker' ? 'block' : 'none';
    viewManage.style.display = viewName === 'manage' ? 'block' : 'none';
    viewSettings.style.display = viewName === 'settings' ? 'block' : 'none';

    // Toggle nav active state
    navChecker.classList.toggle('active', viewName === 'checker');
    navManage.classList.toggle('active', viewName === 'manage');
    navSettings.classList.toggle('active', viewName === 'settings');

    if (viewName === 'manage') renderManagement();
}

async function fetchProjects() {
    try {
        const response = await fetch('/api/projects');
        projects = await response.json();
        renderProjectSidebar();
        renderProjectSelector();
        if (currentView === 'manage') renderManagement();
    } catch (error) {
        console.error('Failed to fetch projects:', error);
    }
}

// --- Rendering ---
function renderProjectSidebar() {
    projectList.innerHTML = '';
    projects.forEach(p => {
        const li = document.createElement('li');
        li.className = currentProject && currentProject.name === p.name ? 'active' : '';
        li.textContent = p.name;
        li.onclick = () => selectProject(p);
        projectList.appendChild(li);
    });
}

async function selectProject(project) {
    currentProject = project;
    renderProjectSidebar();

    // Sync the header dropdown if it exists
    const projSelect = document.getElementById('header-project-selector');
    if (projSelect) projSelect.value = project.name;

    // Fetch environments for the selected project
    try {
        const response = await fetch(`/api/projects/${project.name}/environments`);
        const envs = await response.json();
        renderEnvSelector(envs);
    } catch (error) {
        console.error('Failed to fetch environments:', error);
    }
}

function renderProjectSelector() {
    displayProject.innerHTML = '';
    const select = document.createElement('select');
    select.id = 'header-project-selector';
    select.className = 'scope-selector';
    select.innerHTML = '<option value="">Select Project</option>';

    projects.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name;
        opt.textContent = p.name;
        if (currentProject && currentProject.name === p.name) opt.selected = true;
        select.appendChild(opt);
    });

    select.onchange = (e) => {
        const proj = projects.find(p => p.name === e.target.value);
        if (proj) selectProject(proj);
    };

    displayProject.appendChild(select);
}

function renderEnvSelector(envs) {
    displayEnv.innerHTML = '';

    const select = document.createElement('select');
    select.id = 'header-env-selector';
    select.className = 'scope-selector';
    select.innerHTML = '<option value="">Select Env</option>';

    envs.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.name;
        opt.textContent = e.name;
        select.appendChild(opt);
    });

    select.onchange = (e) => {
        currentEnv = e.target.value;
    };

    displayEnv.appendChild(select);
    if (envs.length > 0) {
        select.value = envs[0].name;
        currentEnv = envs[0].name;
    }
}

function renderManagement() {
    projectsListBody.innerHTML = '';
    projects.forEach(p => {
        const tr = document.createElement('tr');
        const date = new Date(p.created_at).toLocaleDateString();
        tr.innerHTML = `
            <td><strong>${p.name}</strong></td>
            <td><div class="req-preview" title="${p.requirements || ''}">${p.requirements || 'No requirements defined.'}</div></td>
            <td>${date}</td>
            <td>
                <button class="action-btn" onclick="openEditProject('${p.name}')">Edit</button>
                <button class="action-btn" onclick="showEnvManagement('${p.name}')">Envs</button>
                <button class="action-btn delete" onclick="deleteProject('${p.name}')">Delete</button>
            </td>
        `;
        projectsListBody.appendChild(tr);
    });
}

window.deleteProject = async (name) => {
    if (!confirm(`Are you sure you want to delete project '${name}' and all its data?`)) return;
    try {
        await fetch(`/api/projects/${name}`, { method: 'DELETE' });
        if (currentProject && currentProject.name === name) {
            currentProject = null;
            currentEnv = null;
            displayProject.textContent = 'Select Project';
            displayEnv.innerHTML = 'Select Env';
        }
        await fetchProjects();
    } catch (error) { console.error('Delete failed:', error); }
};

window.openEditProject = (name) => {
    const p = projects.find(proj => proj.name === name);
    if (!p) return;
    modalProjectName.value = p.name;
    modalProjectReqs.value = p.requirements || '';
    projectModal.style.display = 'flex';
};

window.showEnvManagement = async (name) => {
    const p = projects.find(proj => proj.name === name);
    if (!p) return;

    currentProject = p; // Ensure we track which project we are managing envs for
    envManageCard.style.display = 'block';
    envManageProjectName.textContent = p.name;

    try {
        const response = await fetch(`/api/projects/${p.name}/environments`);
        const envs = await response.json();
        envsListBody.innerHTML = '';

        envs.forEach(e => {
            const tr = document.createElement('tr');
            const date = new Date(e.created_at).toLocaleDateString();
            tr.innerHTML = `
                <td>${e.name}</td>
                <td>${date}</td>
                <td>
                    <button class="action-btn" onclick="clearEnvironmentPrompts('${p.name}', '${e.name}')">Clear Prompts</button>
                    <button class="action-btn delete" onclick="deleteEnvironment('${p.name}', '${e.name}')">Delete</button>
                </td>
            `;
            envsListBody.appendChild(tr);
        });

        // Scroll to the env card
        envManageCard.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Failed to fetch envs:', error);
    }
};

window.clearEnvironmentPrompts = async (projectName, envName) => {
    if (!confirm(`Are you sure you want to delete ALL saved prompts in environment '${envName}'? This cannot be undone.`)) return;
    try {
        const resp = await fetch(`/api/projects/${projectName}/environments/${envName}/prompts`, { method: 'DELETE' });
        const data = await resp.json();
        alert(data.message);
    } catch (error) {
        console.error('Clear prompts failed:', error);
        alert('Failed to clear prompts');
    }
};

window.deleteEnvironment = async (projectName, envName) => {
    if (!confirm(`Delete environment '${envName}'?`)) return;
    try {
        await fetch(`/api/projects/${projectName}/environments/${envName}`, { method: 'DELETE' });
        if (currentProject && currentProject.name === projectName && currentEnv === envName) {
            currentEnv = null;
            displayEnv.innerHTML = 'Select Env';
        }
        await showEnvManagement(projectName);
        await selectProject(currentProject); // Refresh UI list
    } catch (error) { console.error('Env delete failed:', error); }
};

// --- Checker Logic ---
async function runAnalysis() {
    if (!currentProject || !currentEnv) {
        resultsArea.innerHTML = `
            <div class="card animated" style="padding: 32px; text-align: center; border: 1px dashed var(--border);">
                <div style="font-size: 2rem; margin-bottom: 16px;">📁</div>
                <h3 style="margin-bottom: 8px;">No Project or environment Selected</h3>
                <p style="color: var(--text-dim);">Please select a project from the sidebar and an environment from the top bar to analyze your prompt.</p>
            </div>
        `;
        return;
    }

    const prompt = promptEditor.value.trim();
    if (!prompt) {
        alert('Please enter a prompt to analyze.');
        return;
    }

    resultsArea.innerHTML = '<div class="loading">Analyzing Prompt Quality & Similarity...</div>';

    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project: currentProject.name,
                environment: currentEnv,
                prompt: prompt,
                url: lmStudioUrlInput.value
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Analysis failed');
        }

        const data = await response.json();
        renderResults(data);
    } catch (error) {
        let errorMsg = error.message;
        let actionBtn = '';
        if (errorMsg.includes('Dimension mismatch')) {
            actionBtn = `<button class="primary-btn sm" style="margin-top: 12px; background: #ef4444;" onclick="resetPromptDatabase()">Reset Prompt Database</button>`;
        }
        resultsArea.innerHTML = `
            <div class="card animated" style="padding: 24px; color: #f87171; text-align: center;">
                <div>Analysis failed: ${errorMsg}</div>
                ${actionBtn}
            </div>
        `;
    }
}

window.resetPromptDatabase = async () => {
    if (!confirm("This will PERMANENTLY DELETE all saved prompts to change the database dimension to match your current model. Continue?")) return;

    const prompt = promptEditor.value.trim() || "test";
    try {
        const response = await fetch('/api/debug/reset-prompts', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project: currentProject ? currentProject.name : 'default',
                environment: currentEnv ? currentEnv : 'default',
                prompt: prompt,
                url: lmStudioUrlInput.value
            })
        });
        const data = await response.json();
        alert(data.message || "Database reset successfully");
        runAnalysis();
    } catch (error) {
        alert("Reset failed: " + error.message);
    }
};

function renderResults(data) {
    resultsArea.innerHTML = '';

    // Requirements
    const reqCard = document.createElement('div');
    reqCard.className = 'result-card card animated';
    const analysisText = data.requirement_analysis || "";
    let isPass = analysisText.includes('NO ISSUES');
    reqCard.innerHTML = `
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
            <h3>Requirement Compliance</h3>
            <span class="badge ${isPass ? 'success' : 'warning'}">${isPass ? 'PASSED' : 'CONFLICTS'}</span>
        </div>
        <div class="card-body" style="padding: 24px;">
            <p style="white-space: pre-wrap; font-size: 0.95rem; line-height: 1.6;">${analysisText || "No requirements analysis performed."}</p>
        </div>
    `;
    resultsArea.appendChild(reqCard);

    // Similarity
    const simCard = document.createElement('div');
    simCard.className = 'result-card card animated';
    const wasSaved = data.was_saved;
    simCard.innerHTML = `
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
            <h3>Similarity matches</h3>
            <div style="display: flex; gap: 12px; align-items: center;">
                <span class="badge ${data.similar_prompts.length > 0 ? 'warning' : 'success'}">${data.similar_prompts.length} Matches</span>
                <button id="save-to-db-btn" class="secondary-btn" style="padding: 4px 12px; font-size: 0.75rem;" ${wasSaved ? 'disabled' : ''}>
                    ${wasSaved ? 'Saved ✓' : 'Save to Database'}
                </button>
            </div>
        </div>
        <div class="card-body" style="padding: 24px;">
            ${data.similar_prompts.length === 0 ? '<p style="color: var(--text-dim);">No similar prompts found in this environment. Prompt automatically saved.</p>' : ''}
            <div style="display: flex; flex-direction: column; gap: 16px;">
                ${data.similar_prompts.map(p => {
        const date = new Date(p.created_at);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `
                    <div style="background: rgba(0,0,0,0.2); border-radius: 12px; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.8rem; color: var(--text-dim);">
                            <span style="color: var(--primary); font-weight: 600;">${(p.similarity * 100).toFixed(1)}% Similarity</span>
                            <div>
                                <span style="margin-right: 12px;">${formattedDate}</span>
                                <span>ID: ${p.id}</span>
                            </div>
                        </div>
                        <p style="font-size: 0.85rem; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.5;">${p.prompt_text}</p>
                    </div>
                `}).join('')}
            </div>
        </div>
    `;
    resultsArea.appendChild(simCard);

    // Attach save event if not already saved
    const saveBtn = document.getElementById('save-to-db-btn');
    if (wasSaved) {
        saveBtn.style.color = '#10b981';
        saveBtn.style.borderColor = '#10b981';
    } else {
        saveBtn.onclick = () => savePrompt(data.prompt_text);
    }
}

async function savePrompt(promptText) {
    if (!currentProject || !currentEnv) return;
    const saveBtn = document.getElementById('save-to-db-btn');
    saveBtn.textContent = 'Saving...';
    saveBtn.disabled = true;

    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project: currentProject.name,
                environment: currentEnv,
                prompt: promptText,
                url: lmStudioUrlInput.value
            })
        });

        if (response.ok) {
            saveBtn.textContent = 'Saved ✓';
            saveBtn.style.color = '#10b981';
            saveBtn.style.borderColor = '#10b981';
        } else {
            const errData = await response.json();
            throw new Error(errData.detail || 'Save failed');
        }
    } catch (error) {
        let msg = error.message;
        if (msg.includes('Dimension mismatch')) {
            msg = 'Dimension mismatch. Please run "Analyze Prompt" to reset.';
        }
        saveBtn.textContent = 'Error: ' + msg;
        saveBtn.title = error.message;
        saveBtn.disabled = false;
        console.error(error);
    }
}

// --- Event Listeners ---
function setupEventListeners() {
    navChecker.onclick = (e) => { e.preventDefault(); switchView('checker'); };
    navManage.onclick = (e) => { e.preventDefault(); switchView('manage'); };
    navSettings.onclick = (e) => { e.preventDefault(); switchView('settings'); };

    lmStudioUrlInput.oninput = () => {
        localStorage.setItem('lm-studio-url', lmStudioUrlInput.value);
    };

    runCheckBtn.onclick = runAnalysis;

    addProjectBtn.onclick = () => {
        modalProjectName.value = '';
        modalProjectReqs.value = '';
        projectModal.style.display = 'flex';
    };

    manageAddProjectBtn.onclick = () => addProjectBtn.click();

    manageAddEnvBtn.onclick = () => {
        if (!currentProject) { alert('Select a project first'); return; }
        modalEnvName.value = '';
        envModal.style.display = 'flex';
    };

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.onclick = () => {
            projectModal.style.display = 'none';
            envModal.style.display = 'none';
        };
    });

    saveProjectBtn.onclick = async () => {
        const name = modalProjectName.value.trim();
        const requirements = modalProjectReqs.value.trim();
        if (!name) return;

        try {
            await fetch('/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, requirements })
            });
            projectModal.style.display = 'none';
            await fetchProjects();
        } catch (error) { console.error('Save failed:', error); }
    };

    saveEnvBtn.onclick = async () => {
        const name = modalEnvName.value.trim();
        if (!name || !currentProject) return;

        try {
            await fetch('/api/environments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_name: currentProject.name, name })
            });
            envModal.style.display = 'none';
            await showEnvManagement(currentProject.name);
            await selectProject(currentProject); // Refresh UI
        } catch (error) { console.error('Env save failed:', error); }
    };

    // PDF Import
    const importPdfBtn = document.getElementById('import-pdf-btn');
    const pdfUpload = document.getElementById('pdf-upload');
    importPdfBtn.onclick = (e) => { e.preventDefault(); pdfUpload.click(); };
    pdfUpload.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        importPdfBtn.textContent = 'Extracting...';
        try {
            const resp = await fetch('/api/projects/import-pdf', { method: 'POST', body: formData });
            const res = await resp.json();
            if (res.text) modalProjectReqs.value = res.text;
        } catch (err) { console.error(err); }
        finally { importPdfBtn.textContent = 'Import PDF'; pdfUpload.value = ''; }
    };
}

init();
