from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any

app = FastAPI(title="LangGraph - Demo Graph Executor")

class Node(BaseModel):
    id: str
    skill_url: str
    operation: str

class Graph(BaseModel):
    name: str
    nodes: List[Node]
    edges: List[Dict[str,str]] = []

@app.post("/execute_graph")
async def execute_graph(graph: Graph, payload: Dict[str, Any]):
    # Very simple sequential executor: call nodes in listed order
    results = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        for node in graph.nodes:
            url = f"{node.skill_url.rstrip('/')}/{node.operation.lstrip('/')}"
            # prepare node_input: include profile and previous outputs
            node_input = {"profile": payload.get("profile", {}), **results}
            try:
                r = await client.post(url, json=node_input)
                r.raise_for_status()
                res = r.json()
                results[node.id] = res.get("output", res)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Node {node.id} failed: {e}")
    return {"graph": graph.name, "results": results}
