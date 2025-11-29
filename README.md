# Medical Bill Extraction API 🏥

High-accuracy medical bill extraction API using **Gemini 2.0 Flash** via **OpenRouter** for the HackRx Datathon.

[![API Status](https://img.shields.io/badge/status-active-success.svg)](http://localhost:8000)
[![Model](https://img.shields.io/badge/model-Gemini%202.0%20Flash-blue.svg)](https://openrouter.ai)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

## 🎯 Features

- ✅ **Gemini 2.0 Flash** - Latest AI model via OpenRouter
- ✅ **Multi-format Support** - PDF and images (PNG, JPG, JPEG, WEBP, etc.)
- ✅ **Duplicate Detection** - Prevents double-counting items across pages
- ✅ **Validation System** - Compares calculated vs extracted totals
- ✅ **Sub-total Extraction** - Extracts section-wise subtotals
- ✅ **Final Total Extraction** - Extracts grand total from bill
- ✅ **Accuracy Metrics** - Match percentage and discrepancy tracking

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jaiyankargupta/hacks.git
cd hacks
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment

```bash
# Create .env file
echo "OPENROUTER_API_KEY=your_openrouter_api_key" > .env
```

### 4. Run the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

## 📡 API Usage

### POST /extract-bill-data

Extract line items from medical bills.

**Request:**
```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://example.com/bill.pdf"
  }'
```

**Response:**
```json
{
  "is_success": true,
  "token_usage": {
    "total_tokens": 1234,
    "input_tokens": 1000,
    "output_tokens": 234
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "Paracetamol 500mg",
            "item_amount": 50.00,
            "item_rate": 5.00,
            "item_quantity": 10.00
          }
        ]
      }
    ],
    "section_wise_subtotals": [
      {
        "section_name": "Pharmacy",
        "subtotal": 50.00,
        "item_count": 1
      }
    ],
    "final_total": 50.00,
    "total_item_count": 1
  },
  "validation": {
    "has_final_total": true,
    "calculated_total": 50.00,
    "extracted_total": 50.00,
    "match_percentage": 100.0,
    "has_discrepancy": false,
    "discrepancy_amount": 0.0,
    "duplicate_count": 0
  }
}
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

### GET /

Simple status check.

```bash
curl http://localhost:8000/
```

## 🧠 How It Works

### Architecture

```
Document URL → Fetch → Detect Type → Encode Base64 → 
OpenRouter API (Gemini 2.0 Flash) → Parse JSON → 
Validate → Return Results
```

### Accuracy Strategy

1. **Enhanced Prompt Engineering**
   - Detailed instructions for extracting ALL line items
   - Explicit duplicate detection rules
   - Sub-total and final total extraction
   - Validation requirements

2. **Multi-Step Validation**
   ```python
   calculated_total = sum(all_line_items)
   extracted_total = final_total_from_bill
   match_percentage = accuracy_metric
   ```

3. **Duplicate Detection**
   - Creates fingerprint: `item_name + item_amount`
   - Tracks items across pages
   - Prevents double-counting

4. **Comprehensive Schema**
   - Page-wise line items
   - Section-wise subtotals
   - Final total
   - Validation metrics

## 📊 Response Schema

```json
{
  "is_success": "boolean",
  "token_usage": {
    "total_tokens": "integer",
    "input_tokens": "integer",
    "output_tokens": "integer"
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "string",
        "page_type": "Bill Detail | Final Bill | Pharmacy",
        "bill_items": [
          {
            "item_name": "string",
            "item_amount": "float",
            "item_rate": "float",
            "item_quantity": "float"
          }
        ]
      }
    ],
    "section_wise_subtotals": [
      {
        "section_name": "string",
        "subtotal": "float",
        "item_count": "integer"
      }
    ],
    "final_total": "float",
    "total_item_count": "integer"
  },
  "validation": {
    "has_final_total": "boolean",
    "calculated_total": "float",
    "extracted_total": "float",
    "match_percentage": "float",
    "has_discrepancy": "boolean",
    "discrepancy_amount": "float",
    "duplicate_count": "integer"
  }
}
```

## 🔧 Configuration

### OpenRouter Setup

1. Get API key from [OpenRouter](https://openrouter.ai/)
2. Add to `.env` file:
   ```
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

### Model Configuration

Currently using: `google/gemini-2.0-flash-exp:free`

To change model, edit `app.py`:
```python
"model": "google/gemini-2.0-flash-exp:free"  # Change here
```

Available models on OpenRouter:
- `google/gemini-2.0-flash-exp:free` (Free tier)
- `google/gemini-pro-1.5` (Paid)
- `anthropic/claude-3.5-sonnet` (Paid)
- And many more...

## 📈 Performance Metrics

Expected performance on medical bills:

| Metric | Target | Strategy |
|--------|--------|----------|
| **Accuracy** | 92-95% | Enhanced prompt + validation |
| **Speed** | 2-4 sec | Gemini 2.0 Flash optimization |
| **Cost** | FREE | Using free tier |
| **Duplicate Prevention** | 100% | Fingerprint detection |
| **Total Match** | >95% | Mathematical validation |

## 🧪 Testing

### Run Test Script

```bash
python test_api.py
```

### Manual Testing

```bash
# Test with sample bill
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.pdf"
  }'
```

## 🐛 Troubleshooting

### Issue: API key not configured
```bash
# Check .env file
cat .env

# Should contain:
OPENROUTER_API_KEY=sk-or-v1-...
```

### Issue: Server not responding
```bash
# Check if server is running
curl http://localhost:8000/health

# Restart server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Issue: Low match percentage
- Check if bill has multiple summary pages (duplicate items)
- Verify final total is clearly visible
- Check for discount/tax items

## 📁 Project Structure

```
.
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env.example          # Environment template
├── setup.sh              # Setup script
├── test_api.py           # Test script
├── README.md             # This file
├── IMPLEMENTATION.md     # Technical details
├── QUICKSTART.md         # Quick start guide
└── .gitignore           # Git ignore
```

## 🔐 Security

- ✅ `.env` file is in `.gitignore`
- ✅ API keys never committed to Git
- ✅ Use environment variables for secrets
- ✅ Validate input URLs before processing

## 📄 License

MIT License - Feel free to use for the hackathon!

## 🙏 Acknowledgments

- **OpenRouter** - Unified API for AI models
- **Google Gemini** - Powerful vision AI
- **FastAPI** - Modern Python web framework
- **HackRx Datathon** - Problem statement

## 📞 Support

For issues or questions:
- Check the [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details
- Review [QUICKSTART.md](QUICKSTART.md) for setup help
- Open an issue on GitHub

---

**Built with ❤️ using Gemini 2.0 Flash via OpenRouter for HackRx Datathon**

**Live Demo**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs  
**Health Check**: http://localhost:8000/health
