# 🏛️ System Architecture - 12TH.ai

## 🔭 Overview

**12TH.ai** is an AI-powered educational platform designed to assist A/L students in Sri Lanka with Physics, Chemistry, and Combined Mathematics. The system leverages a **Retrieval-Augmented Generation (RAG)** architecture to provide accurate, syllabus-aligned answers by querying a vector database of course materials before generating responses with Google's Gemini AI.

## 🏗️ High-Level Architecture

The system follows a microservices-inspired, modular monolith architecture with a clear separation between the presentation layer (Frontend) and the business logic/data layer (Backend).

```mermaid
graph TD
    User[Student / User] -->|HTTPS| FE[Frontend (Next.js)]
    
    subgraph "Frontend Layer"
        FE -->|Auth| NextAuth[NextAuth.js]
        FE -->|API Calls| BE_API[Backend API (FastAPI)]
        FE -->|WebSocket| BE_WS[WebSocket Service]
    end
    
    subgraph "Backend Layer (FastAPI)"
        BE_API --> AuthServ[Auth Service]
        BE_API --> RAGServ[RAG Service]
        BE_API --> UserServ[User Service]
        BE_WS --> RAGServ
    end
    
    subgraph "Data Layer"
        AuthServ -->|Read/Write| DB[(PostgreSQL)]
        UserServ -->|Read/Write| DB
        RAGServ -->|Vector Search| PGVector[(PostgreSQL + pgvector)]
        RAGServ -->|Content Retrieval| DB
    end
    
    subgraph "External Services"
        NextAuth -->|OAuth| GoogleAuth[Google OAuth 2.0]
        RAGServ -->|Generation| Gemini[Google Gemini API]
    end
```

## 🧩 Key Components

### 1. Frontend (`frontend/admin-dashboard`)
Built with **Next.js 14+ (App Router)**, offering a responsive and interactive user experience.
- **Framework**: React, Next.js
- **Styling**: Tailwind CSS, shadcn/ui
- **State Management**: SWR (Stale-While-Revalidate) for data fetching.
- **Authentication**: NextAuth.js configured with Google Provider.
- **Real-time**: Custom WebSocket hooks for streaming AI responses.

### 2. Backend (`backend-new -add features/backend`)
A high-performance **FastAPI** application structured for modularity and scalability.
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy (Async)
- **Migrations**: Alembic
- **API Documentation**: OpenAPI (Swagger UI)

#### Modular Structure
The backend is organized into domain-specific modules:
- `app/routers`: API route definitions (Subjects, Theories, Past Papers).
- `app/services`: Business logic (RAG pipeline, WebSocket handling).
- `app/crud`: Database operations.
- `app/models`: SQLAlchemy database models.
- `app/schemas`: Pydantic models for request/response validation.

### 3. Database Layer
The system utilizes **PostgreSQL** as the unified database solution for both structured and unstructured data.
- **Structured Data**: Users, Conversations, Messages, Subjects, Papers.
- **Vector Store**: **pgvector** extension for storing and querying high-dimensional embeddings of course materials.
    - *Note*: Replaces separate vector stores like ChromaDB/Weaviate for simplified infrastructure.

### 4. AI & RAG Engine
- **LLM**: Google Gemini (Pro/Flash models) via `google-generativeai` SDK.
- **Embeddings**: Google's embedding models (e.g., `embedding-001`) generate vectors for course content.
- **RAG Pipeline**:
    1.  **Ingestion**: PDFs and textual content are chunked, embedded, and stored in PostgreSQL (pgvector).
    2.  **Retrieval**: User queries are embedded and matched against stored vectors using cosine similarity.
    3.  **Generation**: Retrieved context + User Query are sent to Gemini to generate the final answer.

## 🔄 Data Flow

### Chat & RAG Workflow
1.  **User Input**: Student asks a question via the chat interface.
2.  **WebSocket Connection**: Message sent over secure WebSocket to Backend.
3.  **Vector Search**:
    - Backend generates an embedding for the query.
    - Queries **PostgreSQL (pgvector)** for top-k relevant content chunks.
4.  **Context Assembly**: Retrieved chunks are formatted into a prompt context.
5.  **AI Generation**: Prompt sent to **Gemini API**.
6.  **Streaming Response**: AI response is streamed back token-by-token to the Frontend via WebSocket.
7.  **Persistance**: Conversation history is saved to PostgreSQL.

## 🛠️ Infrastructure & Deployment

- **Docker**: Both Frontend and Backend are containerized.
- **Docker Compose**: Orchestrates the services (Frontend, Backend, PostgreSQL) for local development and deployment.
- **Environment**: Configured via `.env` files for secure credential management.

## 🔐 Security

- **Authentication**: OAuth 2.0 (Google) ensures secure login.
- **Session Management**: JWT (JSON Web Tokens) used for API authorization.
- **CORS**: Strictly configured to allow requests only from the trusted frontend origin.
