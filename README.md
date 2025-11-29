# Medical Bill Extraction API

High-accuracy medical bill extraction API using **Gemini 2.0 Flash** for the HackRx Datathon.

## 🎯 Features

- ✅ **Gemini 2.0 Flash Experimental** - Latest and most accurate model
- ✅ **Multi-format Support** - PDF and images (PNG, JPG, JPEG, WEBP, etc.)
- ✅ **Duplicate Detection** - Prevents double-counting items across pages
- ✅ **Validation System** - Compares calculated vs extracted totals
- ✅ **Sub-total Extraction** - Extracts section-wise subtotals
- ✅ **Final Total Extraction** - Extracts grand total from bill
- ✅ **Accuracy Metrics** - Match percentage and discrepancy tracking

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Run the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### POST /extract-bill-data

Extract line items from medical bills.

**Request:**
```json
{
  "document": "https://example.com/bill.pdf"
}
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

### GET /

Health check endpoint.

### GET /health

Detailed health status.

## 🧠 How It Works

### 1. **Enhanced Prompt Engineering**
- Detailed instructions for extracting ALL line items
- Explicit duplicate detection rules
- Sub-total and final total extraction
- Validation requirements

### 2. **Multi-Step Processing**
```
Document URL → Fetch → Detect Type → Upload to Gemini → 
Extract with AI → Parse JSON → Validate → Return Results
```

### 3. **Validation System**
- Calculates total from line items
- Compares with extracted final total
- Flags discrepancies > ₹1
- Detects duplicate items across pages

### 4. **Duplicate Detection**
- Creates fingerprint: `item_name + item_amount`
- Tracks items across pages
- Prevents double-counting

## 📊 Accuracy Features

| Feature | Description |
|---------|-------------|
| **Calculated Total** | Sum of all line item amounts |
| **Extracted Total** | Final total from bill |
| **Match Percentage** | Accuracy metric (target: >95%) |
| **Duplicate Count** | Number of duplicate items detected |
| **Missing Data** | Tracks items with missing rate/quantity |

## 🔧 Configuration

### Model Selection
Currently using: `gemini-2.0-flash-exp`

To change model, edit `app.py`:
```python
model="gemini-2.0-flash-exp"  # Change here
```

### Validation Threshold
Default: 90% match required

To adjust, edit `app.py`:
```python
if validation.get('match_percentage', 0) < 90:  # Change threshold
```

## 📝 Testing

### Using cURL
```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{"document": "https://example.com/bill.pdf"}'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/extract-bill-data",
    json={"document": "https://example.com/bill.pdf"}
)
print(response.json())
```

## 🎯 Optimization Tips

1. **For Complex Bills**: The model automatically handles multi-page documents
2. **For Better Accuracy**: Ensure bills are clear and readable
3. **For Speed**: Use smaller image sizes when possible
4. **For Cost**: Gemini 2.0 Flash is already optimized for cost

## 🐛 Troubleshooting

### Issue: Low match percentage
- Check if bill has multiple summary pages (duplicate items)
- Verify final total is clearly visible
- Check for discount/tax items

### Issue: Missing items
- Ensure all pages are included in PDF
- Check if items are in tabular format
- Verify image quality is good

### Issue: Model timeout
- Reduce image size
- Check internet connection
- Verify Gemini API quota

## 📈 Performance Metrics

Expected performance on medical bills:
- **Accuracy**: 92-95%
- **Speed**: 2-4 seconds per document
- **Cost**: ~$0.0005 per document

## 🔐 Security

- Never commit `.env` file
- Use environment variables for API keys
- Validate input URLs before processing

## 📄 License

MIT License - Feel free to use for the hackathon!

## 👥 Support

For issues or questions, check the code comments or raise an issue.

---

**Built with ❤️ using Gemini 2.0 Flash for HackRx Datathon**
