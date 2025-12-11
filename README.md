# 🚀 RAG Web Application

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen.svg)

**A modern Retrieval-Augmented Generation (RAG) web application with document management and intelligent chat capabilities.**

[Demo](#) · [Report Bug](https://github.com/Myrythm/rag-web-gpt/issues) · [Request Feature](https://github.com/Myrythm/rag-web-gpt/issues)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)

---

## ✨ Features

### 🎯 Core Functionality

- **📄 Document Upload & Management** - Upload PDF documents and automatically chunk them for RAG
- **💬 Intelligent Chat** - Ask questions and get answers based on your uploaded documents
- **🔍 Vector Search** - Used ChromaDB for semantic similarity search
- **📊 Admin Dashboard** - Manage users and documents
- **🔐 Authentication & Authorization** - Secure login with role-based access control (Admin/User)
- **📱 Responsive Design** - Works well on all devices

### 🛠️ Advanced Features

- **Pagination** - Efficient data browsing for large datasets
- **Search & Filter** - Find users and documents quickly
- **Chat History** - Persistent conversation storage with session management
- **Real-time Updates** - Dynamic content loading without page refresh

---

## 🛠️ Tech Stack

### Backend

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[LangChain](https://python.langchain.com/)** - LLM orchestration framework (v1.0)
- **[ChromaDB](https://www.trychroma.com/)** - Vector database for embeddings
- **[SQLite](https://www.sqlite.org/)** - Lightweight database for user & metadata storage
- **[OpenAI API](https://openai.com/)** - GPT models for chat completion and embedding

### Frontend

- **[Vue 3](https://vuejs.org/)** - Progressive JavaScript framework
- **[Pinia](https://pinia.vuejs.org/)** - State management
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Vue Router](https://router.vuejs.org/)** - Official router for Vue.js
- **[Axios](https://axios-http.com/)** - HTTP client

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **npm or yarn** - Comes with Node.js
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

---

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Myrythm/rag-web-gpt.git
cd rag-web-gpt
```

### 2️⃣ Backend Setup

#### Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Initialize Database & Create Admin User

```bash
python create_admin.py
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
```

---

## ⚙️ Configuration

### Environment Variables

rename `.env.example` to `.env` and add required API key in the root directory:

```env
OPENAI_API_KEY=sk-proj-.....
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls.....
```

## 🎮 Usage

### Running the Application

#### Start Backend Server

```bash
# Make sure you're in the root directory with venv activated
uvicorn backend.main:app --reload
```

The backend API will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### Default Admin Credentials

After running `create_admin.py`, you can log in with:

- **Username**: `admin` (or the one you created)
- **Password**: (the one you set)

---

## 📁 Project Structure

```
rag-web-gpt/
├── backend/
│   ├── chains/                     # LangChain RAG logic
│   │   ├── rag_chain.py            # RAG chain with streaming support
│   │   └── retriever_chroma.py     # ChromaDB retriever
│   ├── routes/                     # API endpoints
│   │   ├── admin.py                # Admin management endpoints
│   │   ├── auth.py                 # Authentication endpoints
│   │   └── chat.py                 # Chat endpoints
│   ├── services/                   # Business logic
│   │   ├── chroma_client.py        # ChromaDB client
│   │   ├── chunker.py              # Text chunking for documents
│   │   ├── embedding_model.py      # OpenAI embeddings
│   │   ├── langsmith_client.py     # LangSmith tracing
│   │   └── sqlite_client.py        # SQLite database operations
│   ├── utils/                      # Utilities
│   │   ├── config.py               # App configuration
│   │   └── security.py             # Auth & JWT handling
│   └── main.py                     # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/              # Admin dashboard components
│   │   │   │   ├── DocumentsSection.vue
│   │   │   │   ├── OverviewSection.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── UsersSection.vue
│   │   │   ├── chat/               # Chat components
│   │   │   │   ├── ChatInput.vue
│   │   │   │   ├── ChatMessage.vue
│   │   │   │   └── MarkdownRenderer.vue
│   │   │   └── common/             # Shared components
│   │   │       └── Pagination.vue
│   │   ├── pages/                  # Page components
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── Login.vue
│   │   │   └── UserChat.vue
│   │   ├── router/                 # Vue Router configuration
│   │   ├── stores/                 # Pinia state management
│   │   │   ├── chat.js             # Chat state
│   │   │   ├── theme.js            # Theme state
│   │   │   └── user.js             # User auth state
│   │   ├── utils/                  # Frontend utilities
│   │   ├── App.vue                 # Root component
│   │   └── main.js                 # Vue entry point
│   └── index.html                  # Main HTML file
├── chroma/                         # ChromaDB vector storage (auto-generated)
├── .env                            # Environment variables (create this)
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore rules
├── create_admin.py                 # Script to create admin user
├── requirements.txt                # Python dependencies
└── README.md                       # You are here!
```

---

<div align="center">
  
**⭐ Star this repo if you find it helpful!**

</div>
