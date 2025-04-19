# 🧠 AI Study Assistant - FastAPI Backend

This FastAPI backend powers the AI Study Assistant app, enabling intelligent, session-aware interactions with LLMs like GPT-4. It supports both general-purpose chat and YouTube summarization, integrates with Firestore for persistent session storage, and is optionally extendable with vector search (via CassIO + AstraDB) for Retrieval-Augmented Generation (RAG).

---

## 🔧 Features

- **LLM-based chat** with session history
- **YouTube transcript summarization**
- **Session-based memory** via Firestore
- **RESTful API endpoints** for easy integration
- **Optional RAG capabilities** using CassIO + AstraDB
- CORS enabled for frontend communication

---

## 🚀 Endpoints

### `POST /chat`
- Handles user queries with history
- Accepts: `user_query`, `session`, `mode`
- Returns: AI-generated `answer`

### `POST /summarize`
- Summarizes YouTube transcripts
- Accepts: `ytlink`, `session`
- Returns: `summary`

---

## 📁 Directory Structure

```
.
├── app.py              # Main FastAPI app
├── models.py           # LLM logic: chat, summarization
├── requirements.txt    # Python dependencies
└── ...
```

---

## 🧠 Tech Stack

- **FastAPI** - High-performance Python API framework
- **Pydantic** - Data validation
- **Firestore** - Realtime chat/message storage
- **OpenAI API** - LLM processing (e.g., GPT-4)
- **CassIO + AstraDB** *(optional)* - Vector DB for RAG
- **Uvicorn** - ASGI server

---

## 🛠️ Setup Instructions

1. **Clone the repo**
```bash
git clone https://github.com/your-username/ai-study-assistant-fastapi.git
cd ai-study-assistant-fastapi
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the server**
```bash
uvicorn app:app --reload --port 8000
```

---

## 🔐 Environment Variables
Create a `.env` file or set the following variables:
```
OPENAI_API_KEY=your_openai_key
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=...
FIREBASE_CLIENT_EMAIL=...
```

---

## 🌐 Used With
- Frontend: [Next.js App](https://github.com/your-username/ai-study-assistant-nextjs)
- PDF Export: html2pdf.js
- Markdown Rendering: ReactMarkdown + rehype-highlight

---

## 📄 License
MIT

---

## 🙌 Acknowledgements
- [FastAPI](https://fastapi.tiangolo.com)
- [OpenAI](https://openai.com)
- [Firebase](https://firebase.google.com)
- [DataStax AstraDB](https://www.datastax.com/astra)

---

> Built with ❤️ for students who love to learn smarter, not harder.
