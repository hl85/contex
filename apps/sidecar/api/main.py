from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add project root to path to import core
sys.path.append(os.getcwd())
from apps.sidecar.core.docker_client import docker_client
from apps.sidecar.core.logger import get_logger, get_logs, clear_logs
from apps.sidecar.core.config import config_manager

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

@app.post("/notify")
async def notify_user(request: NotificationRequest):
    # In a real scenario, this would communicate with the Tauri main process
    # For MVP, we'll just log it to stdout which Tauri can capture
    logger.info(f"[NOTIFICATION] Title: {request.title} | Content: {request.content}")
    return {"status": "sent"}

@app.post("/run-task")
async def run_task(request: TaskRequest):
    logger.info(f"Received request to run task: {request.task_name}")
    
    if request.task_name == "daily-brief":
        # Prepare environment variables from config
        env_vars = {"SIDECAR_URL": "http://127.0.0.1:12345"}
        
        # Inject GOOGLE_API_KEY if present in config
        api_key = config_manager.get("GOOGLE_API_KEY")
        if api_key:
            env_vars["GOOGLE_API_KEY"] = api_key
            
        # Trigger the docker container
        container_id = docker_client.run_container(
            image="contex-brain:latest",
            command="daily-brief",
            env=env_vars
        )
        return {"status": "started", "container_id": container_id}
    
    logger.warning(f"Task not found: {request.task_name}")
    raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=12345)
