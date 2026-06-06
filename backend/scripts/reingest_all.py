import asyncio
import httpx
import os
import shutil
from pathlib import Path

# Database wiping handled manually to prevent deleting resume chunks
vector_db_path = Path("data/vector_store.json")

REPOS = [
    "https://github.com/akashgaikwad28/RTI_Agents",
    "https://github.com/akashgaikwad28/CommerceLens-AI",
    "https://github.com/akashgaikwad28/PratibimbAI",
    "https://github.com/akashgaikwad28/Capgemini-HMS-Backend",
    "https://github.com/akashgaikwad28/lms-chatbot",
    "https://github.com/akashgaikwad28/RakshaNetraAI"
]

API_URL = "http://127.0.0.1:8000/api/v1/ingest/github"
ADMIN_TOKEN = "dev-admin-token"

async def ingest_repo(client: httpx.AsyncClient, repo_url: str):
    print(f"Starting ingestion for {repo_url}...")
    try:
        response = await client.post(
            API_URL,
            headers={"X-Admin-Token": ADMIN_TOKEN},
            json={"repo_url": repo_url, "branch": "main"},
            timeout=120.0
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Success: {data['repo_name']} | Files (READMEs only): {data['files_processed']} | Chunks: {data['chunks_created']}")
        else:
            print(f"[FAIL] Failed: {repo_url} | Status: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {repo_url} | {e}")

async def main():
    print("Restart the backend server first to auto-ingest the smart resume.")
    print("Then running this script will ingest the GitHub READMEs into ChromaDB...")
    
    # Wait for the backend to be available
    async with httpx.AsyncClient() as client:
        try:
            await client.get("http://127.0.0.1:8000/api/v1/health")
        except Exception:
            print("ERROR: Backend server is not running! Please start the backend server and run this script again.")
            return

        for repo in REPOS:
            await ingest_repo(client, repo)
            
    print("Re-ingestion complete! Your RAG pipeline is now clean and smart.")

if __name__ == "__main__":
    asyncio.run(main())
