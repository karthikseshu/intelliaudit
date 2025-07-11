# IntelliAudit - AI-Powered Document Audit Platform

An intelligent document audit platform that uses AI to analyze documents against configurable criteria with human-in-the-loop feedback.

## 🚀 Features

- **Multi-Format Support**: Upload PDF and DOCX documents
- **AI-Powered Analysis**: Uses Gemini, OpenAI, or Hugging Face LLMs
- **Configurable Criteria**: JSON-based audit criteria system
- **Human-in-the-Loop**: Accept/reject audit findings with remarks
- **Professional UI**: Modern, responsive interface
- **Free Deployment**: Deploy on Vercel (frontend) and Render (backend)

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python FastAPI
- **AI Providers**: Gemini (default), OpenAI, Hugging Face
- **Deployment**: Vercel (frontend) + Render (backend)

## 📁 Project Structure

```
IntelliAudit/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── api/            # API calls
│   │   └── config/         # Configuration
│   └── package.json
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core logic
│   │   └── models/        # Data models
│   └── requirements.txt
└── README.md
```

## 🛠️ Local Development

### Prerequisites
- Node.js 18+
- Python 3.8+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Create `.env` files in both directories:

**Backend (.env):**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Running Locally
```bash
# Backend (Terminal 1)
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

Visit: http://localhost:5173

## 🚀 Deployment

### 1. GitHub Repository
1. Create a new repository on GitHub
2. Push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/intelliaudit.git
git push -u origin main
```

### 2. Backend Deployment (Render)
1. Go to [Render.com](https://render.com)
2. Create account and connect GitHub
3. Click "New Web Service"
4. Select your repository
5. Configure:
   - **Name**: intelliaudit-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `LLM_PROVIDER`: gemini
   - `GEMINI_API_KEY`: your_api_key
   - `OPENAI_API_KEY`: your_api_key (optional)
   - `HUGGINGFACE_API_KEY`: your_api_key (optional)

### 3. Frontend Deployment (Vercel)
1. Go to [Vercel.com](https://vercel.com)
2. Create account and connect GitHub
3. Import your repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: dist
5. Add environment variable:
   - `VITE_API_BASE_URL`: https://your-render-app.onrender.com

## 🔧 Configuration

### Adding New Audit Criteria
Edit `backend/app/models/audit_criteria.json`:
```json
[
  {
    "criteria": "Your criteria name",
    "category": "Category",
    "description": "Detailed description",
    "id": "C1"
  }
]
```

### Switching AI Providers
Change `LLM_PROVIDER` in environment variables:
- `gemini` (default, free)
- `openai` (requires API key)
- `huggingface` (requires API key)

## 🎯 API Endpoints

- `POST /api/audit/upload` - Upload document
- `POST /api/audit/run` - Run audit analysis
- `POST /api/llm/prompt` - Direct LLM queries
- `GET /api/config/llm` - Get LLM configuration

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🆘 Support

For issues and questions:
1. Check the [Issues](https://github.com/yourusername/intelliaudit/issues) page
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

**Built with ❤️ using React, FastAPI, and AI** 