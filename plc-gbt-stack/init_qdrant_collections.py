#!/usr/bin/env python3
"""Initialize Qdrant collections for plc-memory system"""


import requests

QDRANT_URL = "http://localhost:6333"

collections = [
    {"name": "python_code", "vector_size": 1536},
    {"name": "documentation", "vector_size": 1536},
    {"name": "configurations", "vector_size": 1536},
]

def create_collection(name, vector_size):
    """Create a Qdrant collection"""
    url = f"{QDRANT_URL}/collections/{name}"
    data = {
        "vectors": {
            "size": vector_size,
            "distance": "Cosine"
        }
    }

    try:
        response = requests.put(url, json=data)
        if response.status_code == 200:
            print(f"✅ Created collection: {name}")
        else:
            print(f"❌ Failed to create {name}: {response.text}")
    except Exception as e:
        print(f"❌ Error creating {name}: {e}")

print("🚀 Initializing Qdrant collections...")
for collection in collections:
    create_collection(collection["name"], collection["vector_size"])
print("✅ Qdrant initialization complete!")
