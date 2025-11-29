#!/bin/bash

# Setup script for Bill Extraction API

echo "🚀 Setting up Bill Extraction API..."
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo ""
echo "🔐 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app:app --reload --host 0.0.0.0 --port 8000"
echo "4. Test: python test_api.py"
echo ""
