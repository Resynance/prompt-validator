from fastapi import FastAPI, HTTPException, Body, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import requests
import os
import pdfplumber
from io import BytesIO
from db_manager import DBManager
from similarity_check import get_embedding, analyze_requirements

VERSION = "0.6.0"

app = FastAPI(title="Prompt Manager API")

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

LM_STUDIO_DEFAULT_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")

class ProjectCreate(BaseModel):
    name: str
    requirements: str
    project_focus: Optional[str] = None

class EnvironmentCreate(BaseModel):
    project_name: str
    name: str

class CheckRequest(BaseModel):
    project: str
    environment: str
    prompt: str
    threshold: float = 0.85
    url: str = LM_STUDIO_DEFAULT_URL
    model: Optional[str] = None

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api/info")
async def get_info():
    """Returns application version and status."""
    return {
        "version": VERSION,
        "status": "healthy",
        "name": "Prompt Similarity Detector"
    }

@app.get("/api/projects")
async def list_projects():
    db = DBManager()
    try:
        with db.conn.cursor(cursor_factory=None) as cur:
            cur.execute("SELECT name, requirements, created_at, project_focus FROM projects ORDER BY name;")
            projects = [{"name": row[0], "requirements": row[1], "created_at": row[2], "project_focus": row[3]} for row in cur.fetchall()]
            return projects
    finally:
        db.close()

@app.delete("/api/projects/{name}")
async def delete_project(name: str):
    db = DBManager()
    try:
        db.delete_project(name)
        return {"message": f"Project '{name}' deleted"}
    finally:
        db.close()

@app.post("/api/projects")
async def create_project(data: ProjectCreate):
    db = DBManager()
    try:
        pid = db.create_project(data.name, data.requirements, data.project_focus)
        return {"id": pid, "name": data.name, "message": "Project created/updated"}
    finally:
        db.close()

@app.patch("/api/projects/{name}")
async def update_project(name: str, data: dict = Body(...)):
    db = DBManager()
    try:
        db.update_project(name, requirements=data.get("requirements"), project_focus=data.get("project_focus"))
        return {"message": f"Project '{name}' updated"}
    finally:
        db.close()

@app.get("/api/projects/{project_name}/environments")
async def list_environments(project_name: str):
    db = DBManager()
    try:
        project = db.get_project(project_name)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        with db.conn.cursor(cursor_factory=None) as cur:
            cur.execute("SELECT name, created_at FROM environments WHERE project_id = %s ORDER BY name;", (project['id'],))
            envs = [{"name": row[0], "created_at": row[1]} for row in cur.fetchall()]
            return envs
    finally:
        db.close()

@app.post("/api/environments")
async def create_environment(data: EnvironmentCreate):
    db = DBManager()
    try:
        eid = db.create_environment(data.project_name, data.name)
        return {"id": eid, "name": data.name, "message": "Environment created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.delete("/api/projects/{project_name}/environments/{env_name}")
async def delete_environment(project_name: str, env_name: str):
    db = DBManager()
    try:
        db.delete_environment(project_name, env_name)
        return {"message": f"Environment '{env_name}' in project '{project_name}' deleted"}
    finally:
        db.close()

@app.delete("/api/projects/{project_name}/environments/{env_name}/prompts")
async def delete_environment_prompts(project_name: str, env_name: str):
    db = DBManager()
    try:
        db.delete_environment_prompts(project_name, env_name)
        return {"message": f"All prompts in environment '{env_name}' (Project: '{project_name}') have been deleted"}
    finally:
        db.close()

@app.post("/api/check")
async def check_prompt(req: CheckRequest):
    db = DBManager()
    try:
        env_data = db.get_environment_by_name(req.project, req.environment)
        if not env_data:
            raise HTTPException(status_code=404, detail=f"Environment '{req.environment}' for project '{req.project}' not found")

        # 1. Requirement Analysis
        req_analysis = analyze_requirements(
            req.prompt, 
            env_data['requirements'], 
            req.url, 
            model_name=req.model,
            project_focus=env_data.get('project_focus')
        )
        
        # 2. Embedding
        embedding = get_embedding(req.prompt, req.url, req.model)
        
        # 3. Similarity Check
        similar = db.find_similar(env_data['id'], embedding, threshold=req.threshold)
        
        # 4. Auto-save if no similar prompts found
        was_saved = False
        if not similar:
            db.save_prompt(env_data['id'], req.prompt, embedding)
            was_saved = True
        
        return {
            "requirement_analysis": req_analysis,
            "similar_prompts": similar,
            "prompt_text": req.prompt,
            "environment_id": env_data['id'],
            "was_saved": was_saved
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        db.close()

@app.post("/api/save")
async def save_prompt(req: CheckRequest):
    db = DBManager()
    try:
        env_data = db.get_environment_by_name(req.project, req.environment)
        if not env_data:
            raise HTTPException(status_code=404, detail=f"Environment '{req.environment}' for project '{req.project}' not found")
        
        embedding = get_embedding(req.prompt, req.url, req.model)
        db.save_prompt(env_data['id'], req.prompt, embedding)
        return {"message": "Prompt saved successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        db.close()

@app.delete("/api/debug/reset-prompts")
async def reset_prompts(req: CheckRequest):
    # We use CheckRequest to get the URL/model to determine the NEW dimension
    db = DBManager()
    try:
        embedding = get_embedding(req.prompt, req.url, req.model)
        dim = len(embedding)
        db.reset_prompts_table(dim)
        return {"message": f"Prompt database reset to {dim} dimensions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/projects/import-pdf")
async def import_pdf_requirements(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        content = await file.read()
        text = ""
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        return {"text": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract PDF text: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
