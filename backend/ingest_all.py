import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend root is in PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent))

# Load .env variables
load_dotenv()

from app.core.config import get_settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import LocalVectorStore
from app.schemas.rag import DocumentChunk

# 1. Resume text content representing Acash's professional profile
resume_text = """
# Acash Gaikwad
Email: akash.gaikwad9945@gmail.com
Phone: +1-555-019-2834
Location: India

## Professional Summary
Staff Software Engineer, AI RAG Architect, and Voice Integration Engineer with over 5 years of experience building production-grade backend APIs, distributed systems, and real-time Conversational Voice AI agents. Expert in Python, FastAPI, TypeScript, Next.js, and LLM orchestration.

## Education
Bachelor of Engineering (B.E.) in Computer Science and Engineering

## Technical Skills
- Programming Languages: Python, JavaScript, TypeScript, SQL, C++, HTML, CSS
- Backend & Frameworks: FastAPI, Flask, Node.js, Express, Uvicorn, RESTful APIs
- Frontend & Styling: Next.js (App Router), React, TailwindCSS, Framer Motion, Shadcn UI, HTML5
- AI & RAG: Gemini Pro, Gemini 2.5 Flash, ChromaDB, vector embeddings, semantic search, hybrid BM25 search, LangGraph
- Voice AI: Vapi, Retell, ElevenLabs, Deepgram (Speech-to-Text), Cartesia (Text-to-Speech), Twilio
- Databases: SQLite, PostgreSQL, MongoDB, Redis, SQLAlchemy, AioSqlite
- Tools & Devops: Docker, Docker-compose, Git, GitHub Actions, AWS, Railway, Linux, Windows

## Key Projects
### Acash AI Interview Assistant (This Project)
- Built an end-to-end recruiter screening assistant featuring a real-time Voice Agent (via Vapi) and a streaming Chat Web UI (via Next.js).
- Designed a hybrid RAG pipeline combining dense vector embeddings (Gemini text-embedding-004) with sparse BM25 keyword matching for 95% retrieval accuracy.
- Integrated Google Calendar API to allow recruiters to verbally or visually check candidate availability and book interviews without human intervention, implementing concurrency locks to prevent double-booking.
- Developed an offline evaluation framework using Deepeval to grade answer faithfulness, context recall, and latency.

### Enterprise RAG Document Parser
- Built a high-throughput document parsing pipeline utilizing PyPDF and GitPython.
- Crawled GitHub repositories recursively to chunk and embed codebases while maintaining syntactical block integrity (classes, functions).
"""

def main():
    settings = get_settings()
    if not settings.gemini_api_key:
        print("Error: GEMINI_API_KEY is not configured in .env.")
        sys.exit(1)

    print("Initializing services...")
    chunker = ChunkingService()
    embedder = EmbeddingService(settings)
    store = LocalVectorStore(settings, embedder)

    print("Ingesting resume...")
    # Chunk resume
    resume_chunks = chunker.chunk_resume(resume_text, "resume.pdf")
    print(f"Generated {len(resume_chunks)} chunks for resume.")
    
    # Ingest
    store.upsert("resume_collection", resume_chunks)
    print("Resume successfully ingested into resume_collection.")

    print("Ingesting local codebase repositories...")
    repo_url = "https://github.com/acash/acash-ai-interview-assistant"
    ignored_dirs = {
        ".git",
        "node_modules",
        ".next",
        "dist",
        "build",
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        "tmp_basetemp",
        "frontend_temp",
    }
    ignored_suffixes = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".lock",
        ".exe",
        ".dll",
        ".db",
    }

    code_chunks = []
    files_processed = 0
    workspace_root = Path(__file__).resolve().parent.parent

    for path in workspace_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.suffix.lower() in ignored_suffixes:
            continue
        if path.name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}:
            continue
        
        # Get relative path for source tracking
        relative_path = path.relative_to(workspace_root).as_posix()
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            file_chunks = chunker.chunk_code_file(content, relative_path, repo_url)
            if file_chunks:
                code_chunks.extend(file_chunks)
                files_processed += 1
        except Exception as e:
            print(f"Skipping {relative_path} due to error: {e}")

    print(f"Processed {files_processed} code files.")
    print(f"Generated {len(code_chunks)} chunks for codebase.")
    
    # Ingest code chunks in batches of 50 to prevent size limits
    batch_size = 50
    for i in range(0, len(code_chunks), batch_size):
        batch = code_chunks[i:i+batch_size]
        store.upsert("github_collection", batch)
        print(f"Ingested code chunk batch {i//batch_size + 1}/{len(code_chunks)//batch_size + 1}...")

    print("Codebase successfully ingested into github_collection.")
    print("All ingestions completed successfully!")

if __name__ == "__main__":
    main()
