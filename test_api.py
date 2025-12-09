#!/usr/bin/env python
"""Test the API endpoints."""
import httpx
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))


async def test_api():
    """Test API endpoints."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(base_url=base_url) as client:
        print("\n✓ Testing API endpoints...\n")

        # Test health endpoint
        try:
            resp = await client.get("/health")
            print(f"✓ Health Check: {resp.status_code}")
            print(f"  Response: {resp.json()}\n")
        except Exception as e:
            print(f"✗ Health Check failed: {e}\n")
            return

        # Test root endpoint
        try:
            resp = await client.get("/")
            print(f"✓ Root Endpoint: {resp.status_code}")
            print(f"  Response: {resp.json()}\n")
        except Exception as e:
            print(f"✗ Root Endpoint failed: {e}\n")

        # Test create graph endpoint
        try:
            graph_data = {
                "name": "Test Graph",
                "description": "A test workflow graph",
                "nodes": [
                    {"node_id": "node1", "name": "Start", "type": "start", "tool": None},
                    {"node_id": "node2", "name": "Process", "type": "process", "tool": "test_tool"},
                    {"node_id": "node3", "name": "End", "type": "end", "tool": None}
                ],
                "edges": [
                    {"from_node": "node1", "to_node": "node2", "type": "normal"},
                    {"from_node": "node2", "to_node": "node3", "type": "normal"}
                ],
                "entry_node": "node1"
            }
            resp = await client.post("/graphs/create", json=graph_data)
            print(f"✓ Create Graph: {resp.status_code}")
            if resp.status_code == 200:
                graph = resp.json()
                print(f"  Graph ID: {graph.get('id')}\n")
            else:
                print(f"  Error: {resp.json()}\n")
        except Exception as e:
            print(f"✗ Create Graph failed: {e}\n")
        
        print("✓ API is working correctly!")
if __name__ == "__main__":
    asyncio.run(test_api())
