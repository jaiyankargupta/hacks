# 🚀 Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
cd /Users/jaiyankargupta/hrx_hacks/billextraction
./setup.sh
```

### 2. Configure API Key
```bash
# Edit .env file
nano .env

# Add your Google API key:
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Start the Server
```bash
# Activate virtual environment
source venv/bin/activate

# Run server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

## Testing

### Option 1: Test Script
```bash
python test_api.py
```

### Option 2: cURL
```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.pdf"
  }'
```

### Option 3: Python
```python
import requests

response = requests.post(
    "http://localhost:8000/extract-bill-data",
    json={"document": "YOUR_DOCUMENT_URL"}
)

result = response.json()
print(f"Success: {result['is_success']}")
print(f"Total Items: {result['data']['total_item_count']}")
print(f"Final Total: ₹{result['data']['final_total']}")
print(f"Accuracy: {result['validation']['match_percentage']}%")
```

## API Endpoints

### POST /extract-bill-data
Main extraction endpoint

**Request:**
```json
{
  "document": "https://example.com/bill.pdf"
}
```

**Response:** See README.md for full schema

### GET /
Health check

### GET /health
Detailed health status

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn app:app --reload --port 8001
```

### API key error
```bash
# Verify .env file exists
cat .env

# Check environment variable
echo $GOOGLE_API_KEY
```

### Dependencies error
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## File Structure

```
billextraction/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your API keys (create this)
├── setup.sh              # Setup script
├── test_api.py           # Test script
├── README.md             # Full documentation
├── IMPLEMENTATION.md     # Technical details
└── QUICKSTART.md         # This file
```

## Next Steps

1. ✅ Test with sample documents
2. ✅ Download training data and test all 15 samples
3. ✅ Measure accuracy and iterate on prompt if needed
4. ✅ Deploy to production (Render, Railway, or Cloud Run)

## Deployment

### Deploy to Render (Free)
1. Push code to GitHub
2. Connect to Render
3. Add environment variable: `GOOGLE_API_KEY`
4. Deploy!

### Deploy to Railway
```bash
railway login
railway init
railway up
```

### Deploy to Google Cloud Run
```bash
gcloud run deploy bill-extraction \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

**Need help?** Check README.md or IMPLEMENTATION.md for details.
