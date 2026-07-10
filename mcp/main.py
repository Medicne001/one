from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MCP - Management Control Plane (demo)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# in-memory registries for demo
SKILLS: Dict[str, Dict[str, Any]] = {}
AUDIT_LOGS = []

class SkillRegistration(BaseModel):
    name: str
    base_url: str
    endpoints: Dict[str, str] = {}

@app.post("/register_skill")
async def register_skill(payload: SkillRegistration):
    SKILLS[payload.name] = {"base_url": payload.base_url, "endpoints": payload.endpoints, "registered_at": time.time()}
    return {"status": "ok", "skill": payload.name}

@app.get("/skills")
async def list_skills():
    return SKILLS

@app.get("/policy/demo")
async def demo_policy():
    # A simple graph: risk_calc -> allocate -> pdf_export
    graph = {
      "name": "demo_buy_house_plan",
      "nodes": [
        {"id":"n1", "skill":"risk_skill", "operation":"risk_calc"},
        {"id":"n2", "skill":"alloc_skill", "operation":"allocate"},
        {"id":"n3", "skill":"pdf_skill", "operation":"pdf_export"}
      ],
      "edges": [
        {"from":"n1","to":"n2"},
        {"from":"n2","to":"n3"}
      ]
    }
    return graph

@app.post("/audit")
async def audit(record: Dict):
    record["received_at"] = time.time()
    AUDIT_LOGS.append(record)
    return {"status":"logged"}

@app.get("/audit_logs")
async def get_logs():
    return AUDIT_LOGS
