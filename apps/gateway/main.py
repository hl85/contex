import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
import sys
import os
from pathlib import Path

# Add project root to path to import core shared logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from apps.sidecar.core.logger import get_logger, setup_logging_config

# Setup Logger (Shared Config)
# Note: In a real microservice, Gateway might have its own logger config, 
# but for MVP we share the file writing logic to aggregate logs.
setup_logging_config()
logger = get_logger("gateway")

app = FastAPI(title="Contex Remote Gateway (WeChat)")

# Configuration
SIDECAR_URL = "http://127.0.0.1:12345"

class WeChatMsg(BaseModel):
    msg_id: str
    sender: str
    content: str
    msg_type: str = "text"

class ReplyMsg(BaseModel):
    recipient: str
    content: str

def process_message_task(msg: WeChatMsg):
    """
    Background task to process message and interact with Sidecar.
    """
    logger.info(f"Processing message from {msg.sender}: {msg.content}")
    
    # 1. Simple Command Parsing
    command = msg.content.strip().lower()
    
    if command.startswith("/brief"):
        # Trigger Daily Brief Skill
        try:
            logger.info("Triggering Daily Brief...")
            # In a real scenario, we might parse topics from the message
            payload = {"task_name": "daily-brief"}
            res = requests.post(f"{SIDECAR_URL}/run-task", json=payload)
            
            if res.status_code == 200:
                send_wechat_reply(msg.sender, "Daily Brief started! I'll update you when it's ready.")
                # Note: Getting the result back requires Sidecar to support Webhooks or polling
                # For MVP, we stop here.
            else:
                send_wechat_reply(msg.sender, f"Failed to start task: {res.text}")
                
        except Exception as e:
            logger.error(f"Error calling Sidecar: {e}")
            send_wechat_reply(msg.sender, "Error connecting to Contex Brain.")
            
    elif command == "/ping":
        send_wechat_reply(msg.sender, "Pong! Gateway is online.")
        
    else:
        send_wechat_reply(msg.sender, f"Unknown command: {command}. Try /brief")

def send_wechat_reply(recipient: str, content: str):
    """
    Mock function to send reply back to WeChat.
    In production, this would call the WeChat API.
    """
    logger.info(f"--- [WECHAT REPLY] To: {recipient} ---\n{content}\n-----------------------")

@app.post("/webhook/wechat")
async def wechat_webhook(msg: WeChatMsg, background_tasks: BackgroundTasks):
    """
    Endpoint to receive messages from WeChat (or a Mock Client).
    """
    logger.info(f"Received WeChat message: {msg}")
    
    # Process in background to reply quickly to WeChat server
    background_tasks.add_task(process_message_task, msg)
    
    return {"status": "received", "msg_id": msg.msg_id}

@app.get("/health")
async def health_check():
    return {"status": "ok", "component": "gateway"}

if __name__ == "__main__":
    # Run on port 12346 to avoid conflict with Sidecar
    uvicorn.run(app, host="127.0.0.1", port=12346)
