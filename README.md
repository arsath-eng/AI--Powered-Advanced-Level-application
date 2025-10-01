# 🎓 12TH.ai - AI-Powered Academic Tutor- It's Ongoing Project

**12TH.ai**  is a full-stack, AI-driven tutoring platform designed to provide accurate, context-aware academic support for Sri Lankan G.C.E. Advanced Level students. It specializes in **Physics**, **Chemistry**, and **Combined Mathematics**, leveraging a powerful Retrieval-Augmented Generation (RAG) system to deliver factually-grounded answers.

---

## ✨ Key Features

* **🧠 Intelligent Chat Interface**: A real-time, streaming chat interface built with Next.js and WebSockets for an interactive learning experience.
* **📚 Retrieval-Augmented Generation (RAG)**: The AI's knowledge is grounded in a vector database (**ChromaDB**) populated with official course materials (PDFs, notes, and structured JSON data) to drastically reduce hallucinations and provide accurate, syllabus-specific answers.
* **🛠️ AI Tool Calling**: The AI can use custom tools to perform precise lookups in a **PostgreSQL** database for specific information, such as fetching a particular past paper question by year, subject, and question number.
* **🔒 Secure Authentication**: End-to-end user authentication using **Google OAuth 2.0** with a JWT-based session management system that includes automatic access/refresh token rotation for long-lasting, secure user sessions.
* **🎨 Rich Media Integration**: Renders relevant images (hosted on Google Drive) and embedded YouTube videos alongside text answers to provide comprehensive, multi-modal explanations.
* **🚀 Production-Ready Architecture**: The entire application is containerized using **Docker** and **Docker Compose**, with a scalable client-server architecture for the vector database, making it ready for cloud deployment.
* **📱 Responsive UI**: A modern, responsive user interface built with **Tailwind CSS** and **shadcn/ui**, featuring a collapsible sidebar and light/dark modes.

---

## 🏛️ Architecture Overview

The application follows a modern, decoupled architecture with a Next.js frontend, a FastAPI backend, and separate services for structured and unstructured data storage.

```
[ User on Browser ]
       |
+----[ Next.js Frontend ]----+
|   (React, NextAuth.js, SWR)  |
+----------------------------+
       |           | (WebSocket)
(REST API)     |
       |           |
+----[ FastAPI Backend ]-----+
|        (Python)            |
+----------------------------+
  |      |        |        |
  |      |        |        +--->[ Google Gemini API ] (Generative AI)
  |      |        |
  |      |        +------------>[ ChromaDB ] (Vector Store for RAG)
  |      |
  |      +---------------------->[ PostgreSQL ] (Structured Data via SQLAlchemy)
  |
  +---------------------------->[ Google OAuth 2.0 ] (Authentication)
```

---

## 💻 Tech Stack

| Category      | Technology                                                                                           |
| :------------ | :--------------------------------------------------------------------------------------------------- |
| **Frontend** | `Next.js`, `React`, `TypeScript`, `Tailwind CSS`, `shadcn/ui`, `SWR`, `NextAuth.js`                    |
| **Backend** | `Python`, `FastAPI`, `SQLAlchemy`, `PostgreSQL`, `Alembic`                                           |
| **AI & ML** | `Google Gemini`, `ChromaDB` (Vector Database), `Sentence Transformers` (Embeddings)                  |
| **DevOps** | `Docker`, `Docker Compose`                                                                           |

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

* Python 3.11+
* Node.js 18+
* Docker and Docker Compose
* A PostgreSQL database instance

### Backend Setup

1. **Clone the repository:**

   ```bash
   git clone <your-repository-url>
   cd <repository-folder>/backend
   ```

2. **Create and configure the environment file:**

   * Rename `.env.example` to `.env`.
   * Fill in the required values for your `DATABASE_URL`, `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GEMINI_API_KEY`.

3. **Install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run Database Migrations:**

   * Ensure your `alembic.ini` is configured with the correct `sqlalchemy.url`.
   * Apply all migrations to set up your database schema:
     ```bash
     alembic upgrade head
     ```

5. **Ingest Data into Vector Store (First Time Only):**

   * Place your JSON data and PDF files in the designated folders.
   * Run the ingestion script:
     ```bash
     python ingest_data.py
     ```

6. **Run the Backend Server:**

   * You can run the app directly with Uvicorn or use the provided Docker setup.
   * **Using Docker (Recommended for Production Simulation):**
     ```bash
     docker-compose up --build
     ```

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd ../frontend 
   ```

2. **Create and configure the environment file:**

   * Rename `.env.local.example` to `.env.local`.
   * Set `NEXT_PUBLIC_API_URL` to `http://localhost:8000`.

3. **Install dependencies:**

   ```bash
   npm install
   ```

4. **Run the Frontend Development Server:**

   ```bash
   npm run dev
   ```

Your application should now be running! Open `http://localhost:3000` in your browser.

---



## 🎯 Use Cases

* **Students**: Get instant, accurate answers to A/L Physics, Chemistry, and Combined Mathematics questions.
* **Self-Study**: Access past paper questions and detailed explanations anytime.
* **Exam Preparation**: Practice with syllabus-aligned content and comprehensive explanations.

---

## 🔐 Environment Variables

### Backend (`.env`)

```ini
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/twelfth_ai

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# AI
GEMINI_API_KEY=your_gemini_api_key

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001
```

### Frontend (`.env.local`)

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📦 Deployment

The application is containerized and ready for deployment on any cloud platform that supports Docker:

* **AWS ECS/Fargate**
* **Google Cloud Run**
* **Azure Container Instances**
* **DigitalOcean App Platform**

---

## Screenshots
<img width="1919" height="912" alt="Al-home" src="https://github.com/user-attachments/assets/5a476913-31c8-4fd0-8bca-f4d62318b510" />
<img width="786" height="607" alt="1" src="https://github.com/user-attachments/assets/2668d28b-0400-4d0b-836f-79275cec55d8" />
<img width="772" height="788" alt="2" src="https://github.com/user-attachments/assets/e45be4e1-5b4c-4f50-abf2-8fc063cec9f7" />
<img width="782" height="698" alt="3" src="https://github.com/user-attachments/assets/095ed400-eff3-4a27-b5de-2ad2d070e2de" />
<img width="801" height="668" alt="4" src="https://github.com/user-attachments/assets/8228dba0-1d25-4f9e-8eed-6b98fb2b3dbb" />






---

