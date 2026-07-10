import os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
load_dotenv()

MCP_URL = os.getenv("MCP_URL", "http://mcp:9000")
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://langgraph:8080")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

app = FastAPI(title="Agent Worker - Demo")

class Profile(BaseModel):
    name: str
    age: int
    goal: str
    horizon_years: int
    risk: str
    assets: dict

@app.post("/run_demo")
async def run_demo(profile: Profile):
    # 1) fetch policy (graph) from MCP
    async with httpx.AsyncClient(timeout=20.0) as client:
        policy = await client.get(f"{MCP_URL}/policy/demo")
        graph = policy.json()
        # resolve skill names to base urls via MCP skill registry
        skills = await client.get(f"{MCP_URL}/skills")
        sk = skills.json()
    # map skill logical names in graph to actual URLs using MCP registry
    name_map = {
        "risk_skill": sk.get("risk_skill", {}).get("base_url"),
        "alloc_skill": sk.get("alloc_skill", {}).get("base_url"),
        "pdf_skill": sk.get("pdf_skill", {}).get("base_url")
    }
    # build langgraph-compatible graph with skill_url fields
    nodes = []
    for n in graph["nodes"]:
        skill_name = n["skill"]
        base = name_map.get(skill_name)
        if not base:
            raise HTTPException(status_code=500, detail=f"skill {skill_name} not registered")
        nodes.append({"id": n["id"], "skill_url": base, "operation": n["operation"]})
    lg_graph = {"name": graph["name"], "nodes": nodes, "edges": graph.get("edges", [])}

    # 2) call LangGraph to execute
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{LANGGRAPH_URL}/execute_graph", json={"name":lg_graph["name"], "nodes":lg_graph["nodes"], "edges":lg_graph["edges"], "payload": {"profile": profile.dict()}})
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail=f"langgraph error: {r.text}")
        out = r.json()

    # 3) combine results and optionally call LLM for human-friendly explanation
    risk_res = out["results"].get("n1", {})
    alloc_res = out["results"].get("n2", {})
    pdf_res = out["results"].get("n3", {})

    explanation = f"Risk score: {risk_res.get('risk_score')} -> allocation: {alloc_res.get('allocation_percent')}"
    # attempt LLM call for nicer wording if key provided
    if OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
                prompt = f"Write a concise, professional summary for this plan. Profile: {profile.dict()} ; risk: {risk_res} ; allocation: {alloc_res}"
                payload = {"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}], "temperature":0.2}
                r = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                if r.status_code == 200:
                    j = r.json()
                    explanation = j["choices"][0]["message"]["content"]
        except Exception as e:
            explanation = explanation + f" (LLM call failed: {e})"

    # 4) write audit to MCP
    audit = {"event":"demo_run","profile":profile.dict(),"results":out["results"], "explanation":explanation, "ts": time.time()}
    async with httpx.AsyncClient() as client:
        await client.post(f"{MCP_URL}/audit", json=audit)

    # return composed response (including pdf/html)
    return {"results": out["results"], "explanation": explanation, "pdf_html": pdf_res.get("html","")}
