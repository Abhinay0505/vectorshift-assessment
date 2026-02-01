# Update main.py with DAG detection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PipelineRequest(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

def is_dag(nodes, edges):
    """Check if graph is a Directed Acyclic Graph using topological sort"""
    if not edges:
        return True
    
    # Build adjacency list and indegree count
    node_ids = [node['id'] for node in nodes]
    adj = {node_id: [] for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        if source in adj:
            adj[source].append(target)
            indegree[target] = indegree.get(target, 0) + 1
    
    # Kahn's topological sort
    queue = [node_id for node_id in node_ids if indegree.get(node_id, 0) == 0]
    visited_count = 0
    
    while queue:
        current = queue.pop(0)
        visited_count += 1
        
        for neighbor in adj.get(current, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    
    return visited_count == len(node_ids)

@app.post('/pipelines/parse')
async def parse_pipeline(request: PipelineRequest):
    nodes = request.nodes
    edges = request.edges
    
    num_nodes = len(nodes)
    num_edges = len(edges)
    is_dag_result = is_dag(nodes, edges)
    
    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'is_dag': is_dag_result
    }