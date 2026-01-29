# 🚀 Quick Setup Guide - LegalRAG India

## Step 1: Download & Extract (YOU ARE HERE)

Download the project starter files and extract them to your local machine.

---

## Step 2: Open in VS Code (5 minutes)

```bash
# Open terminal/command prompt

# Navigate to where you extracted the files
cd path/to/legal-rag-india

# Open in VS Code
code .

# OR just open VS Code and File > Open Folder > select legal-rag-india
```

---

## Step 3: Initialize Git (2 minutes)

```bash
# In VS Code terminal (Ctrl+` or Cmd+`)

# Initialize git
git init

# Check what files we have
git status

# Make first commit
git add .
git commit -m "Initial project setup"
```

---

## Step 4: Create GitHub Repo (3 minutes)

1. Go to https://github.com/new
2. Repository name: `legal-rag-india`
3. Description: `AI-powered legal research assistant for Indian law using RAG`
4. Keep it **Public** (for portfolio)
5. **DON'T** initialize with README (we already have one)
6. Click "Create repository"

Then connect your local repo:

```bash
# Copy the commands GitHub shows you, should be something like:
git remote add origin https://github.com/akshatrksingh/legal-rag-india.git
git branch -M main
git push -u origin main
```

---

## Step 5: Set Up Python Environment (3 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your terminal should now show (venv) at the start

# Install dependencies
pip install -r requirements.txt

# This will take 2-3 minutes
```

---

## Step 6: Get API Keys (5 minutes)

### Groq (Primary LLM - FREE)
1. Go to https://console.groq.com/keys
2. Sign up (use your NYU email)
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### Together AI (Backup - $25 FREE)
1. Go to https://api.together.xyz/
2. Sign up
3. Go to Settings > API Keys
4. Create new key
5. You get $25 free credits automatically

---

## Step 7: Configure Environment (2 minutes)

```bash
# Copy the example env file
cp .env.example .env

# Open .env in VS Code
code .env

# Add your API keys:
GROQ_API_KEY=gsk_your_actual_key_here
TOGETHER_API_KEY=your_together_key_here

# Save the file (Cmd+S or Ctrl+S)
```

---

## Step 8: Test Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Run the server
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.

# Open browser and go to:
# http://localhost:8000
# You should see: {"status": "healthy", "service": "LegalRAG India API", ...}

# Also check the auto-generated API docs:
# http://localhost:8000/docs

# Press Ctrl+C to stop the server
```

---

## ✅ You're All Set!

If everything above worked, you're ready to start building!

**What you have now:**
- ✅ Clean project structure
- ✅ Working FastAPI backend
- ✅ Git initialized & pushed to GitHub
- ✅ Python environment configured
- ✅ API keys ready

**Next Steps:**
1. Build data pipeline (scrape & embed judgments)
2. Implement RAG service
3. Create Streamlit UI
4. Deploy to production

---

## 🆘 Common Issues

**Issue: `python` command not found**
- Try `python3` instead
- Make sure Python 3.10+ is installed

**Issue: venv activation fails on Windows**
- Try: `venv\Scripts\activate.bat`
- Or use PowerShell: `venv\Scripts\Activate.ps1`

**Issue: Permission denied when installing packages**
- Make sure virtual environment is activated (you should see `(venv)`)
- Try: `pip install --user -r requirements.txt`

**Issue: Import errors when running main.py**
- Make sure you're in the `backend/` directory
- Check that venv is activated
- Try reinstalling: `pip install -r ../requirements.txt`

**Issue: Port 8000 already in use**
- Something else is running on port 8000
- Change port in backend/main.py: `uvicorn.run(..., port=8001)`

---

## 📊 Project Overview

**What we're building:**
- Legal Q&A system with verified citations
- Semantic search over 1.4M+ Indian court judgments
- Multi-language support (English/Hindi)
- Zero hallucinations (RAG-based responses)

**Tech Stack:**
- LLM: Groq (Llama 3.3 70B) - 14.4K free requests/day
- Embeddings: bge-large-en-v1.5 (open-source)
- Vector DB: FAISS
- Backend: FastAPI
- Frontend: Streamlit → React
- Deploy: Render (free tier)

**Total Cost: $0/month** ✅

---

**Ready?** Once you've completed all steps above, tell me and we'll start building the core RAG functionality!
