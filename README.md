# CARE-BRIDGE AI

> Your Healthcare Report Assistant - AI-Powered Medical Report Explanation

## 🎯 Features

- **Role-Aware Explanations**: Different views for patients and clinicians
- **Multimodal Report Parsing**: Upload PDF, PNG, or JPG medical reports
- **AI-Powered Analysis**: Google ADK Agent with specialized tools
- **RAG-Enhanced**: Grounded in CDC and RSNA medical guidelines
- **Safety Checks**: Automatic detection of abnormal values
- **Interactive Chat**: Ask questions about your reports
- **Document Management**: Upload, view, and delete reports

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

#### Option 1: Use Batch Files (Windows)

1. Double-click `start_backend.bat` to start the backend server
2. Double-click `start_frontend.bat` to start the frontend

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 📖 Usage

1. **Login**: Enter any email and password (demo mode)
2. **Select Role**: Choose Patient or Clinician mode
3. **Upload Report**: Click "Upload New Report" and select a medical report
4. **View Explanation**: See AI-generated explanation based on your role
5. **Ask Questions**: Use the chat panel to ask about your report
6. **Manage Documents**: Delete old reports from the Manage Documents page

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 5173)
│   (Vite + React)│
└────────┬────────┘
         │ HTTP REST API
         ↓
┌─────────────────┐
│  FastAPI Backend│ (Port 8000)
│                 │
│  ┌───────────┐  │
│  │ Google ADK│  │
│  │   Agent   │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────┴─────┐  │
│  │   Tools   │  │
│  ├───────────┤  │
│  │ • Parser  │  │ (Qwen3-VL)
│  │ • RAG     │  │ (ChromaDB)
│  │ • Safety  │  │ (Rule-based)
│  │ • Explain │  │ (MiroThinker)
│  └───────────┘  │
└─────────────────┘
```

## 🔑 Key Technologies

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite, React Router, Axios |
| Backend | FastAPI, Python 3.8+ |
| AI/ML | Google ADK, Gemini 2.5 Flash, ChromaDB |
| Vector DB | ChromaDB with SentenceTransformers |
| Database | JSON file-based (for demo) |

## 📁 Project Structure

```
AiIgnite/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── start_backend.bat      # Backend startup script
├── start_frontend.bat     # Frontend startup script
├── app/
│   ├── core/              # Core agent & config
│   ├── tools/             # AI tools (parser, RAG, safety, explainer)
│   ├── db/                # Database models
│   └── api/               # API endpoints
├── data/
│   ├── uploads/           # Uploaded reports
│   ├── vector_db/         # ChromaDB storage
│   └── raw_knowledge/     # Medical guidelines
└── frontend/
    ├── src/
    │   ├── pages/         # React pages
    │   ├── services/      # API client
    │   └── App.jsx        # Main app component
    └── package.json       # Node dependencies
```

## 🎨 UI Features

- **Modern Dashboard**: Clean, professional interface
- **Role-Based Views**: Different experiences for patients and clinicians
- **Test Results Table**: Visual display of lab values with status indicators
- **AI Explanations**: Formatted, easy-to-read explanations
- **Real-time Chat**: Ask follow-up questions about your report
- **Document Management**: Full CRUD operations on medical reports

## 🔒 Safety & Compliance

- ✅ Non-diagnostic explanations only
- ✅ Clear disclaimers on all pages
- ✅ Safety checks for abnormal values
- ✅ Citations to medical sources
- ✅ Role-appropriate language

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python dependencies are installed
- Check `requirements.txt` for missing packages

### Frontend won't start
- Check if port 5173 is available
- Run `npm install` in the frontend directory
- Clear npm cache: `npm cache clean --force`

### API connection errors
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify API base URL in `frontend/src/services/api.js`

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/upload-report` | Upload a medical report |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/document/{id}` | Delete a document |
| GET | `/api/explain/{id}` | Get AI explanation |
| POST | `/api/chat/{id}` | Chat about a report |
| POST | `/api/rag/feed` | Add knowledge to RAG |

## 🚧 Future Enhancements

- [ ] Real AI model integration (currently using mock responses)
- [ ] User authentication and authorization
- [ ] PostgreSQL database integration
- [ ] PDF report generation
- [ ] Email notifications
- [ ] Multi-language support
- [ ] EHR system integration
- [ ] Mobile app (React Native)

## 📄 License

This is a demo project for educational purposes.

## 👨‍💻 Author

CARE-BRIDGE AI - Healthcare Report Assistant

---

**Disclaimer**: This application is for demonstration purposes only and should not be used for actual medical diagnosis or treatment.
