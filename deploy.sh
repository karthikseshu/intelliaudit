#!/bin/bash

echo "🚀 IntelliAudit Deployment Script"
echo "=================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: IntelliAudit AI Document Audit Platform"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Next Steps for Deployment:"
echo "=============================="
echo ""
echo "1. 🐙 Create GitHub Repository:"
echo "   - Go to https://github.com/new"
echo "   - Name: intelliaudit"
echo "   - Make it public or private"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. 🔗 Connect to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/intelliaudit.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. 🎯 Deploy Backend to Render:"
echo "   - Go to https://render.com"
echo "   - Sign up/Login with GitHub"
echo "   - Click 'New Web Service'"
echo "   - Connect your GitHub repository"
echo "   - Configure:"
echo "     * Name: intelliaudit-api"
echo "     * Environment: Python 3"
echo "     * Build Command: pip install -r backend/requirements.txt"
echo "     * Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "   - Add Environment Variables:"
echo "     * LLM_PROVIDER: gemini"
echo "     * GEMINI_API_KEY: your_gemini_api_key"
echo ""
echo "4. 🌐 Deploy Frontend to Vercel:"
echo "   - Go to https://vercel.com"
echo "   - Sign up/Login with GitHub"
echo "   - Import your repository"
echo "   - Configure:"
echo "     * Framework Preset: Vite"
echo "     * Root Directory: frontend"
echo "     * Build Command: npm run build"
echo "     * Output Directory: dist"
echo "   - Add Environment Variable:"
echo "     * VITE_API_BASE_URL: https://your-render-app.onrender.com"
echo ""
echo "5. 🔑 Get API Keys:"
echo "   - Gemini: https://makersuite.google.com/app/apikey"
echo "   - OpenAI: https://platform.openai.com/api-keys"
echo "   - Hugging Face: https://huggingface.co/settings/tokens"
echo ""
echo "✅ Your IntelliAudit platform will be live at your Vercel URL!"
echo ""
echo "📚 For detailed instructions, see README.md" 