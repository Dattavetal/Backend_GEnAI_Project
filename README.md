# 🧠 PotpieAI Project – End-to-End RAG Chatbot with Document Ingestion

This project includes two microservices:

- 📄 **document_service**: Handles document upload (.pdf, .docx, .txt), chunks content, generates embeddings, and stores in ChromaDB.
- 💬 **chatbot_service**: Uses Retrieval-Augmented Generation (RAG) to generate intelligent responses based on document context.

---

## 📁 Project Structure

```
PotpieAI_project/
├── chatbot_service/
│   ├── app.py               # Flask app with chat endpoints
│   ├── utils.py             # Functions to retrieve chunks and stream LLM7 response
│   ├── agent_graph.py       # Optional LangGraph implementation for structured reasoning
│   ├── config.py            # (optional config if used)
│  
└── document_service/
│    ├── app.py               # Main Flask application
│    ├── utils.py             # Utility functions for embedding, file reading, and chunking
│    ├── docker-compose.yml   # ChromaDB container
└── requirements.txt
└── README.md    
```

---

## 🛠️ Setup Instructions

### 1. Start ChromaDB

```bash
cd document_service
docker-compose up -d
```

---

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
#### Document Service

```bash
cd document_service
python app.py
```

#### Chatbot Service

```bash
cd chatbot_service
python app.py
```

---

## 📄 Document Upload API

**Endpoint:** `POST /api/documents/process`

```bash
curl --location 'http://127.0.0.1:5001/api/documents/process' \
--form 'file=@"C:/Users/shrey/Desktop/interview/resume/DattatrayVetalResume.pdf"'
```

**Response:**

```json
{
  "asset_id": "24bccbb1-95e2-4840-a0ad-f3d3c470b59f"
}
```

---

## 💬 Chatbot Interaction API

### 1. Start a New Chat

**Endpoint:** `POST /api/chat/start`

```bash
curl --location 'http://127.0.0.1:5002/api/chat/start' \
--header 'Content-Type: application/json' \
--data '{
    "asset_id": "24bccbb1-95e2-4840-a0ad-f3d3c470b59f"
}'
```

**Response:**

```json
{
  "thread_id": "f3c2e00d4b174dc88ae282649ef56c41"
}
```

---

### 2. Send a Chat Message

**Endpoint:** `POST /api/chat/message`

```bash
curl --location 'http://127.0.0.1:5002/api/chat/message' \
--header 'Content-Type: application/json' \
--data '{
    "thread_id": "f3c2e00d4b174dc88ae282649ef56c41",
    "message": "Tell me about this document"
}'
```

Streams response using `text/event-stream`.

---

### 3. Get Chat History

**Endpoint:** `GET /api/chat/history`

```bash
curl --location 'http://127.0.0.1:5002/api/chat/history?thread_id=f3c2e00d4b174dc88ae282649ef56c41'
```

**Response:**

```json
{
  "history": [
    { "role": "user", "content": "Tell me about this document" },
    { "role": "assistant", "content": "The document provides an overview of..." }
  ]
}
```

---

## 🧠 How It Works

### Document Service

1. Upload `.txt`, `.pdf`, `.docx` file.
2. File is read, chunked, embedded.
3. Embeddings are stored in ChromaDB with an `asset_id`.

### Chatbot Service

1. Starts session with given `asset_id`.
2. Retrieves relevant chunks from ChromaDB.
3. Builds prompt and streams LLM7 response via SSE.

---

## 🧪 Agent Graph (Optional)

Run chatbot in terminal with LangGraph:

```bash
cd chatbot_service
python agent_graph.py
```

Follows this flow:

- Retrieve → Prompt → Generate → Respond

---

## 📌 Notes

- ChromaDB must run on `localhost:8000`.
- Ensure the same `asset_id` is used throughout.
- Add volume to `docker-compose.yml` for persistent vector storage.

---
