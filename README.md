<div align="center">
  
# 🤖 Akash AI Interview Assistant

**An intelligent, multi-modal AI agent that acts as a technical representation of Akash Gaikwad.**

[![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248?logo=mongodb)](https://www.mongodb.com/)
[![Vapi](https://img.shields.io/badge/Voice_AI-Vapi-blue)](https://vapi.ai)
[![Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-8E75B2?logo=google)](https://aistudio.google.com/)

[View Live Demo](#) <!-- Replace with your Vercel URL once deployed -->

</div>

---

## 📖 Overview

The **Akash AI Interview Assistant** is an agentic AI platform designed to automate initial technical screenings and act as an interactive portfolio. Recruiters and hiring managers can chat with "Aiden"—an AI persona trained extensively on Akash's resume, technical projects, and background. 

It supports both **text-based chat** and **real-time voice interactions**, and it can autonomously schedule interviews directly onto Akash's Google Calendar.

## ✨ Key Features

- **🗣️ Real-time Voice Agent:** Integrated with Vapi.ai for seamless, low-latency voice conversations.
- **📚 RAG-Powered Knowledge:** Automatically ingests PDF resumes, creates vector embeddings using `gemini-embedding-2`, and stores them in MongoDB for highly accurate context retrieval.
- **📅 Autonomous Scheduling:** Native Google Calendar API integration allows the AI to check availability and securely book interview slots in real-time.
- **💻 Interactive Portfolio:** A beautiful, responsive Next.js frontend showcasing featured projects (RTI Agent, PratibimbAI, etc.) with animated UI components.
- **🛡️ Production Ready:** Configured for one-click deployments to Vercel (Frontend) and Render (Backend) with robust CORS and environment validation.

---

## 🛠️ Technology Stack

### Frontend (Client)
- **Framework:** Next.js (React 19)
- **Styling:** Tailwind CSS + Framer Motion
- **UI Components:** Shadcn UI + Lucide React
- **Voice Integration:** `@vapi-ai/web` SDK

### Backend (Server)
- **Framework:** FastAPI (Python 3.10+)
- **Database:** MongoDB Atlas (Motor Asyncio)
- **AI / LLM:** Google GenAI SDK (`gemini-2.5-flash`)
- **Embeddings:** `gemini-embedding-2`
- **Auth & Integrations:** Google OAuth 2.0 (Calendar API)

---

## 🚀 Architecture

1. **User Interaction:** Users interact via the Next.js frontend (Chat or Voice).
2. **Voice Webhooks:** Vapi captures voice input, transcribes it, and sends a webhook to the FastAPI backend.
3. **Tool Execution:** The backend intercepts tool calls from the LLM (e.g., `get_availability`, `book_slot`, `query_knowledge_base`).
4. **Vector Search:** Queries are embedded and searched against the MongoDB vector store.
5. **Action:** The system either returns factual data about Akash's experience or executes a Google Calendar booking.

---

## ⚙️ Local Development Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend/` directory based on `.env.example`. Then run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```
Create a `.env.local` file in the `frontend/` directory based on `.env.example`. Then run the client:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

---

## 📦 Deployment

The project is structured for seamless CI/CD deployment:
- **Frontend:** Push to GitHub and import the `frontend/` directory into [Vercel](https://vercel.com).
- **Backend:** Create a Web Service on [Render.com](https://render.com) using the root `render.yaml` configuration.

See `docs/deployment_guide.md` (if available) for detailed environment variable setups.

---

## 🤝 Contact

Created by **Akash Gaikwad**.
- **Email:** akash.gaikwad9945@gmail.com
- **LinkedIn:** [Akash Gaikwad](https://linkedin.com/in/akash-santosh-gaikwad)
- **GitHub:** [@akashgaikwad28](https://github.com/akashgaikwad28)
