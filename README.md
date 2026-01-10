# 🏥 CareBridge AI

> An intelligent medical report assistant that helps patients and healthcare providers understand medical documents — **without providing diagnoses**.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

CareBridge AI is a full-stack application that processes medical reports using OCR and AI to provide clear, role-appropriate explanations. The system uses a **RAG (Retrieval-Augmented Generation)** pipeline to store and retrieve document context, ensuring accurate and relevant responses.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart OCR Pipeline** | Extracts text from PDFs and images using Llama Vision models |
| 📚 **RAG-Powered Context** | FAISS vector database for semantic document retrieval |
| 🤖 **MiroThinker AI** | Llama 3.3 70B for intelligent explanations and Q&A |
| 👥 **Role-Based Responses** | Tailored explanations for patients vs. healthcare providers |
| ⚠️ **Safety First** | Strictly no medical diagnoses or treatment recommendations |
| 📄 **Multi-Format Support** | Upload PDF, PNG, JPG medical reports |
| 💬 **Interactive Chat** | Ask questions about your reports in natural language |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                    Dashboard • Chat • Upload                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ REST API
┌─────────────────────────▼───────────────────────────────────────┐
│                     FastAPI Backend                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   OCR       │  │    RAG      │  │     MiroThinker         │  │
│  │  Pipeline   │→ │   Store     │→ │   (Llama 3.3 70B)       │  │
│  │ (Llama VLM) │  │  (FAISS)    │  │  Explain • Chat         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Vite, CSS |
| **Backend** | FastAPI, Uvicorn, Python 3.10+ |
| **OCR** | Llama 3.2 11B Vision (VLM mode), PyPDF |
| **RAG** | FAISS, SentenceTransformers (all-MiniLM-L6-v2) |
| **LLM** | Llama 3.3 70B Instruct via Hugging Face Router API |
| **Database** | JSON file storage for metadata |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Hugging Face API key with **write** access

### 1. Clone the Repository

```bash
git clone https://github.com/sakthi44710/care-bridge.git
cd care-bridge
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
HF_API_KEY=your_huggingface_api_key_here
PORT=8000
```

### 4. Start Backend

```bash
cd app
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## 📡 API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/documents` | List all uploaded documents |
| `POST` | `/api/documents/upload` | Upload a medical report (PDF/image) |
| `GET` | `/api/documents/{id}` | Get document details |
| `DELETE` | `/api/documents/{id}` | Delete a document |

### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/explain` | Get AI explanation of a report |
| `POST` | `/api/chat` | Chat with MiroThinker about reports |

### Example: Chat Request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does my hemoglobin level mean?",
    "document_id": "doc_123",
    "role": "patient"
  }'
```

### Example: Response

```json
{
  "response": "Your hemoglobin level indicates how much oxygen your blood can carry. I can help explain what the numbers mean, but please consult your doctor for any medical advice.",
  "ai_powered": true,
  "context_used": true
}
```

---

## 🔒 Safety & Ethics

CareBridge AI is designed with strict safety guidelines:

| ✅ **Will Do** | ❌ **Won't Do** |
|---------------|----------------|
| Explain medical terminology | Provide diagnoses |
| Summarize report contents | Recommend treatments |
| Answer general health questions | Interpret test results medically |
| Clarify what tests measure | Replace professional medical advice |

Every AI response includes a reminder to consult healthcare professionals for medical decisions.

---

## 📁 Project Structure

```
AiIgnite/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   └── endpoints.py     # API route handlers
│   ├── core/
│   │   ├── agent.py         # AI agent logic
│   │   └── config.py        # Configuration
│   ├── db/
│   │   ├── database.py      # Database operations
│   │   └── models.py        # Data models
│   ├── tools/
│   │   ├── explainer.py     # Explanation generation
│   │   ├── parser.py        # Document parsing
│   │   ├── rag.py           # RAG operations
│   │   └── safety.py        # Safety filters
│   └── utils/
│       └── formatter.py     # Response formatting
├── data/
│   ├── db.json              # Document metadata
│   ├── uploads/             # Uploaded files
│   └── vector_db/           # FAISS index storage
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── pages/           # Page components
│   │   └── services/        # API client
│   └── package.json
├── requirements.txt
└── README.md
```

---

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_API_KEY` | Hugging Face API key | Required |
| `PORT` | Backend server port | `8000` |
| `HF_LLM_MODEL_ID` | LLM model for chat/explain | `meta-llama/Llama-3.3-70B-Instruct` |
| `HF_OCR_VLM_MODEL_ID` | Vision model for OCR | `meta-llama/Llama-3.2-11B-Vision-Instruct` |
| `HF_OCR_MODE` | OCR mode (`vlm` or `ocr`) | `vlm` |

### Model Fallback Chain

If the primary model is unavailable, the system falls back to:
1. `meta-llama/Llama-3.3-70B-Instruct` (primary)
2. `Qwen/Qwen2.5-7B-Instruct` (fallback)

---

## 🧪 Development

### Run Backend Tests

```bash
cd app
python -m pytest tests/
```

### Code Quality

```bash
# Python linting
pip install ruff
ruff check app/

# Frontend linting
cd frontend
npm run lint
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

**CareBridge AI is not a substitute for professional medical advice, diagnosis, or treatment.** Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of information provided by this application.

---

<p align="center">
  Made with ❤️ for better healthcare understanding
</p>