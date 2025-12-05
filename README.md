# 🎓 12TH.ai - AI-Powered Academic Tutor

**12TH.ai**  is a full-stack, AI-driven tutoring platform designed to provide accurate, context-aware academic support for Sri Lankan G.C.E. Advanced Level students. It specializes in **Physics**, **Chemistry**, and **Combined Mathematics**, leveraging a powerful Retrieval-Augmented Generation (RAG) system to deliver factually-grounded answers.

---

## ✨ Key Features

* **🧠 Intelligent Chat Interface**: A real-time, streaming chat interface built with Next.js and WebSockets for an interactive learning experience.
* **📚 Retrieval-Augmented Generation (RAG)**: The AI's knowledge is grounded in a vector database (**PostgreSQL pgvector**) populated with official course materials (PDFs, notes, and structured JSON data) to drastically reduce hallucinations and provide accurate, syllabus-specific answers.
* **🛠️ AI Tool Calling**: The AI can use custom tools to perform precise lookups in a **PostgreSQL** database for specific information, such as fetching a particular past paper question by year, subject, and question number.
* **🔒 Secure Authentication**: End-to-end user authentication using **Google OAuth 2.0** with a JWT-based session management system that includes automatic access/refresh token rotation for long-lasting, secure user sessions.
* **🎨 Rich Media Integration**: Renders relevant images (hosted on Google Drive) and embedded YouTube videos alongside text answers to provide comprehensive, multi-modal explanations.
* **🚀 Production-Ready Architecture**: The entire application is containerized using **Docker** and **Docker Compose**, with a scalable client-server architecture for the vector database, making it ready for cloud deployment.
* **📱 Responsive UI**: A modern, responsive user interface built with **Tailwind CSS** and **shadcn/ui**, featuring a collapsible sidebar and light/dark modes.

---

## 🏛️ Architecture Overview

For a comprehensive deep-dive into the system's technical design, including component interactions and data flow diagrams, please refer to the [Architecture Documentation](architecture.md).

---

## 💻 Tech Stack

| Category      | Technology                                                                                           |
| :------------ | :--------------------------------------------------------------------------------------------------- |
| **Frontend** | `Next.js`, `React`, `TypeScript`, `Tailwind CSS`, `shadcn/ui`, `SWR`, `NextAuth.js`                    |
| **Backend** | `Python`, `FastAPI`, `SQLAlchemy`, `PostgreSQL`, `Alembic`                                           |
| **AI & ML** | `Google Gemini`, `PostgreSQL pgvector` (Vector Database), `Sentence Transformers` (Embeddings)                  |
| **DevOps** | `Docker`, `Docker Compose`                                                                           |

---

## 🚀 Getting Started

Follow these step-by-step instructions to set up the project locally.

### Prerequisites

*   **Python 3.11+**: Ensure Python is installed and added to your PATH.
*   **Node.js 18+**: Required for the Next.js frontend.
*   **PostgreSQL 15+**: You need a running PostgreSQL instance with the `pgvector` extension installed.
*   **Git**: For cloning the repository.

### 1. Clone the Repository

```bash
git clone https://github.com/arsath-eng/AI--Powered-Advanced-Level-application.git
cd AI--Powered-Advanced-Level-application
```

### 2. Backend Setup

navigate to the backend directory:

```bash
cd "backend-new -add features/backend"
```

**Create Virtual Environment:**

```bash
python -m venv venv
# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**Install Dependencies:**

```bash
pip install -r requirements.txt
```

**Environment Configuration:**

1.  Create a `.env` file in the `backend-new -add features/backend` directory.
2.  Paste the following configuration (update with your actual credentials):

    ```ini
    # Database (Ensure pgvector is enabled on this DB)
    DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/twelfth_ai

    # Security
    SECRET_KEY=your_super_secret_key_openssl_rand_hex_32
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    # Google OAuth
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # AI Services
    GEMINI_API_KEY=your_google_gemini_api_key
    ```

**Initialize Database:**

```bash
# Run Alembic migrations to create tables
alembic upgrade head
```

**Run the Server:**

```bash
uvicorn app.main:app --reload
```

The backend will start at `http://localhost:8000`.

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend/admin-dashboard
```

**Environment Configuration:**

1.  Create a `.env.local` file.
2.  Add the following:

    ```ini
    NEXT_PUBLIC_API_URL=http://localhost:8000
    NEXTAUTH_URL=http://localhost:3000
    NEXTAUTH_SECRET=your_nextauth_secret
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    ```

**Install Dependencies & Run:**

```bash
npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

---



## 🧠 Prompt Engineering & Context Management
 
 This system uses a sophisticated prompt engineering strategy to ensure high-quality, syllabus-compliant responses.
 
 ### 1. System Constitution (`UNIFIED_SYSTEM_PROMPT`)
 The AI is given a core identity "A/L Thōzhan" (A/L Scholar) via a rigid system instructions block. This "Constitution" defines:
 *   **Persona:** An expert Sri Lankan A/L Tutor.
 *   **Language:** Tamil primary response with English technical terms.
 *   **Formatting:** Strict LaTeX rules for all math ($x$, $$E=mc^2$$) and markdown structure.
 *   **Tone:** Helpful, precise, and educational.
 
 ### 2. Dynamic Context Injection
 When a user asks a question, the system dynamically assembles the prompt using RAG:
 
 *   **Retrieval:** The user's query is vectorized to search the PostgreSQL (`pgvector`) database for relevant theories, past paper questions, or textbook content.
 *   **History:** The conversation history is pulled from the `conversations` table to maintain context (e.g., "Explain *that* step again").
 *   **Assembly:** These components are injected into scenario-specific templates:
 
 ### 3. Prompt Templates
 The backend switches between different templates based on the intent:
 
 *   **`PAST_PAPER_TEMPLATE`**: Used when discussing specific exam questions. It forces the AI to structure the answer with "Question", "Relevant Theories", "Step-by-Step Solution", and "Final Answer".
 *   **`THEORY_EXPLANATION_TEMPLATE`**: Used for conceptual questions, mandating "Definition", "Equations", and "Explanation" sections.
 *   **`ESSAY_QUESTION_TEMPLATE`**: Handles multi-part structured essay questions, ensuring each part is answered individually before summarizing.
 
 This structured approach prevents "AI hallucination" and ensures the output is always formatted correctly for the frontend's LaTeX renderer.

This system uses a sophisticated prompt engineering strategy to ensure high-quality, syllabus-compliant responses.

### 1. System Constitution (`UNIFIED_SYSTEM_PROMPT`)
The AI is given a core identity "A/L Thōzhan" (A/L Scholar) via a rigid system instructions block. This "Constitution" defines:
*   **Persona:** An expert Sri Lankan A/L Tutor.
*   **Language:** Tamil primary response with English technical terms.
*   **Formatting:** Strict LaTeX rules for all math ($x$, $$E=mc^2$$) and markdown structure.
*   **Tone:** Helpful, precise, and educational.

### 2. Dynamic Context Injection
When a user asks a question, the system dynamically assembles the prompt using RAG:

*   **Retrieval:** The user's query is vectorized to search the PostgreSQL (`pgvector`) database for relevant theories, past paper questions, or textbook content.
*   **History:** The conversation history is pulled from the `conversations` table to maintain context (e.g., "Explain *that* step again").
*   **Assembly:** These components are injected into scenario-specific templates:

### 3. Prompt Templates
The backend switches between different templates based on the intent:

*   **`PAST_PAPER_TEMPLATE`**: Used when discussing specific exam questions. It forces the AI to structure the answer with "Question", "Relevant Theories", "Step-by-Step Solution", and "Final Answer".
*   **`THEORY_EXPLANATION_TEMPLATE`**: Used for conceptual questions, mandating "Definition", "Equations", and "Explanation" sections.
*   **`ESSAY_QUESTION_TEMPLATE`**: Handles multi-part structured essay questions, ensuring each part is answered individually before summarizing.

This structured approach prevents "AI hallucination" and ensures the output is always formatted correctly for the frontend's LaTeX renderer.

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

