from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys
import json
import glob
from pathlib import Path

# Add project root to path to import core
sys.path.append(os.getcwd())

# Initialize Config first to load .env
from apps.sidecar.core.config import config_manager
from apps.sidecar.core.docker_client import docker_client
from apps.sidecar.core.logger import get_logger, get_logs, clear_logs, setup_logging_config

# Setup Global Logging
setup_logging_config()
logger = get_logger("sidecar.api")

app = FastAPI(title="Contex Sidecar")

# Enable CORS for Frontend Development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NotificationRequest(BaseModel):
    title: str
    content: str

class TaskRequest(BaseModel):
    task_name: str

class ConfigRequest(BaseModel):
    config: dict

@app.get("/health")
async def health_check():
    return {"status": "ok", "component": "sidecar"}

@app.get("/logs")
async def fetch_logs():
    return get_logs(200)

@app.delete("/logs")
async def clear_logs_endpoint():
    clear_logs()
    return {"status": "cleared"}

@app.get("/config")
async def get_config():
    return config_manager.get_all()

@app.post("/config")
async def update_config(request: ConfigRequest):
    if config_manager.save(request.config):
        return {"status": "saved"}
    raise HTTPException(status_code=500, detail="Failed to save config")

# --- Skills Management ---

@app.get("/skills")
async def list_skills():
    """Scan packages/skills and return manifests."""
    skills = []
    skills_dir = Path(os.getcwd()) / "packages/skills"
    
    # Find all manifest.json files
    manifests = glob.glob(str(skills_dir / "*/manifest.json"))
    
    for m_path in manifests:
        try:
            with open(m_path, "r") as f:
                manifest = json.load(f)
                skills.append(manifest)
        except Exception as e:
            logger.error(f"Failed to load manifest {m_path}: {e}")
            
    return skills

@app.get("/config/{skill_id}")
async def get_skill_config(skill_id: str):
    """Get config for a specific skill."""
    all_config = config_manager.get_all()
    skill_configs = all_config.get("skill_configs", {})
    return skill_configs.get(skill_id, {})

@app.post("/config/{skill_id}")
async def update_skill_config(skill_id: str, request: ConfigRequest):
    """Update config for a specific skill."""
    all_config = config_manager.get_all()
    if "skill_configs" not in all_config:
        all_config["skill_configs"] = {}
    
    all_config["skill_configs"][skill_id] = request.config
    
    if config_manager.save(all_config):
        return {"status": "saved"}
    raise HTTPException(status_code=500, detail="Failed to save config")

# -------------------------

@app.post("/notify")
async def notify_user(request: NotificationRequest):
    # In a real scenario, this would communicate with the Tauri main process
    # For MVP, we'll just log it to stdout which Tauri can capture
    logger.info(f"[NOTIFICATION] Title: {request.title} | Content: {request.content}")
    return {"status": "sent"}

@app.post("/run-task")
async def run_task(request: TaskRequest):
    logger.info(f"Received request to run task: {request.task_name}")
    
    # Prepare base environment variables
    env_vars = {"SIDECAR_URL": "http://127.0.0.1:12345"}
    
    # 1. Inject Global Config (API Keys)
    api_key = config_manager.get("GOOGLE_API_KEY")
    if api_key:
        env_vars["GOOGLE_API_KEY"] = api_key
        
    # 2. Inject Skill Config
    all_config = config_manager.get_all()
    skill_configs = all_config.get("skill_configs", {})
    skill_specific_config = skill_configs.get(request.task_name, {})
    
    if skill_specific_config:
        env_vars["SKILL_CONFIG"] = json.dumps(skill_specific_config)
        
    # Trigger the docker container
    # Assuming task_name matches folder name in packages/skills/
    container_id = docker_client.run_container(
        image="contex-brain:latest",
        command=request.task_name,
        env=env_vars
    )
    
    if container_id:
        return {"status": "started", "container_id": container_id}
    else:
        logger.warning(f"Task not found or failed to start: {request.task_name}")
        raise HTTPException(status_code=404, detail="Task not found or failed to start")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=12345)
