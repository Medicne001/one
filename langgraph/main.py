from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any

app = FastAPI(title="LangGraph - Demo Graph Executor")

class Condition(BaseModel):
    op: str
    path: str
    value: Any

class Node(BaseModel):
    id: str
    skill_url: str
    operation: str
    condition: Dict[str, Any] = None

class Graph(BaseModel):
    name: str
    nodes: List[Node]
    edges: List[Dict[str,str]] = []


def eval_condition(cond: Dict[str, Any], results: Dict[str, Any]) -> bool:
    if not cond:
        return True
    op = cond.get('op')
    path = cond.get('path')  # e.g., 'n1.risk_score'
    value = cond.get('value')
    # simple path resolution
    parts = path.split('.') if path else []
    cur = results
    try:
        for p in parts:
            cur = cur.get(p) if isinstance(cur, dict) else None
    except Exception:
        cur = None
    if cur is None:
        return False
    if op == 'equals':
        return cur == value
    if op == 'gt':
        return cur > value
    if op == 'lt':
        return cur < value
    return False

@app.post("/execute_graph")
async def execute_graph(graph: Graph, payload: Dict[str, Any]):
    # Sequential executor with simple condition support
    results = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        for node in graph.nodes:
            # evaluate condition if present
            if node.condition:
                if not eval_condition(node.condition, results):
                    # skip node
                    results[node.id] = {'skipped': True}
                    continue
            url = f"{node.skill_url.rstrip('/')}/{node.operation.lstrip('/')}"
            node_input = {"profile": payload.get("profile", {}), **results}
            try:
                r = await client.post(url, json=node_input)
                r.raise_for_status()
                res = r.json()
                results[node.id] = res.get("output", res)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Node {node.id} failed: {e}")
    return {"graph": graph.name, "results": results}
