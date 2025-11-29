from PIL import Image
import io
import json
import traceback
import os
import base64
from typing import Dict, Any, List, Optional
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

load_dotenv() 

app = FastAPI(title="Medical Bill Extraction API", version="1.0.0")

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class DocumentInput(BaseModel):
    document: HttpUrl 

# Enhanced prompt for maximum accuracy with sub-totals and final totals
PROMPT = """You are an expert medical bill extraction system. Extract ALL line items with PERFECT accuracy.

CRITICAL REQUIREMENTS:
1. Extract EVERY single line item - missing items = FAILURE
2. DO NOT double-count items (check if item appears on both detail and summary pages)
3. Extract sub-totals per section (Pharmacy, Diagnostics, Room charges, etc.)
4. Extract the FINAL TOTAL from the bill
5. Ensure calculated total matches extracted total

OUTPUT SCHEMA (JSON ONLY, NO MARKDOWN):
{
  "is_success": boolean,
  "token_usage": {
    "total_tokens": integer,
    "input_tokens": integer,
    "output_tokens": integer
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "string",
        "page_type": "Bill Detail | Final Bill | Pharmacy",
        "bill_items": [
          {
            "item_name": "string",
            "item_amount": float,
            "item_rate": float,
            "item_quantity": float
          }
        ]
      }
    ],
    "section_wise_subtotals": [
      {
        "section_name": "string",
        "subtotal": float,
        "item_count": integer
      }
    ],
    "final_total": float,
    "total_item_count": integer
  }
}

EXTRACTION RULES:
1. **Line Items**: Extract ONLY actual billable items, NOT sub-totals or grand totals
2. **Item Name**: Copy EXACTLY as printed (join multi-line with single space)
3. **Item Amount**: Net amount after discounts (required, use -1 if missing)
4. **Item Rate**: Unit price (use -1 if not shown)
5. **Item Quantity**: Quantity (use -1 if not shown)
6. **Page Type**: 
   - "Pharmacy" = medicine/drug items
   - "Bill Detail" = detailed breakdown with line items
   - "Final Bill" = summary page with totals
7. **Section Sub-totals**: Extract sub-totals for sections like:
   - Pharmacy, Diagnostics, Radiology, Pathology, Room Charges, Consultation, etc.
8. **Final Total**: Extract the GRAND TOTAL from the bill
9. **Duplicate Detection**: If same item appears on multiple pages:
   - Count it ONLY ONCE (prefer detail page over summary page)
   - Mark in your analysis but don't include twice

VALIDATION CHECKS:
- Sum of all item_amounts should equal final_total (within ₹1 tolerance)
- Sum of section subtotals should equal final_total
- total_item_count must match actual count of bill_items
- No item should appear twice with same name and amount

EDGE CASES:
- Discount items: Include as negative amounts
- Tax items: Include as separate line items
- Multi-line item names: Join with single space
- Missing rate/quantity: Set to -1
- Items without amount: Set to -1

EXAMPLE OUTPUT:
{
  "is_success": true,
  "token_usage": {
    "total_tokens": -1,
    "input_tokens": -1,
    "output_tokens": -1
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "Paracetamol 500mg Tablet",
            "item_amount": 50.00,
            "item_rate": 5.00,
            "item_quantity": 10.00
          },
          {
            "item_name": "Complete Blood Count (CBC)",
            "item_amount": 400.00,
            "item_rate": 400.00,
            "item_quantity": 1.00
          }
        ]
      }
    ],
    "section_wise_subtotals": [
      {
        "section_name": "Pharmacy",
        "subtotal": 50.00,
        "item_count": 1
      },
      {
        "section_name": "Diagnostics",
        "subtotal": 400.00,
        "item_count": 1
      }
    ],
    "final_total": 450.00,
    "total_item_count": 2
  }
}

IMPORTANT: 
- Return ONLY valid JSON (no markdown, no code blocks, no explanations)
- All numbers must be numeric types (not strings)
- Set is_success=true ONLY if extraction is complete and accurate
- If you cannot extract final_total, set it to -1
"""

def detect_file_type(url: str, content: bytes, headers):
    """Detect file type from URL, headers, or content"""
    ct = headers.get("content-type", "").lower()
    if "pdf" in ct:
        return "application/pdf", "pdf"
    if ct.startswith("image/"):
        return ct, "image"

    lower = url.lower()
    if lower.endswith(".pdf"):
        return "application/pdf", "pdf"
    if any(lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff")):
        ext_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
            ".tiff": "image/tiff",
        }
        return ext_map.get(lower[-5:], "image/jpeg"), "image"

    if content[:4] == b"%PDF":
        return "application/pdf", "pdf"

    try:
        img = Image.open(io.BytesIO(content))
        mime = f"image/{img.format.lower()}"
        return mime, "image"
    except Exception:
        pass

    return "application/octet-stream", "unknown"


def detect_duplicates(pagewise_items: List[Dict]) -> List[Dict]:
    """Detect duplicate items across pages"""
    seen_items = {}
    duplicates = []
    
    for page in pagewise_items:
        for item in page.get('bill_items', []):
            # Create fingerprint: name + amount
            fingerprint = f"{item['item_name'].strip().lower()}_{item['item_amount']}"
            
            if fingerprint in seen_items:
                # Potential duplicate found
                duplicates.append({
                    'item': item,
                    'page_no': page['page_no'],
                    'original_page': seen_items[fingerprint]['page_no']
                })
            else:
                seen_items[fingerprint] = {
                    'item': item,
                    'page_no': page['page_no']
                }
    
    return duplicates


def validate_extraction(data: Dict) -> Dict:
    """Validate extraction accuracy and add validation metadata"""
    validation = {
        "has_final_total": False,
        "calculated_total": 0.0,
        "extracted_total": 0.0,
        "match_percentage": 0.0,
        "has_discrepancy": True,
        "discrepancy_amount": 0.0,
        "duplicate_count": 0,
        "missing_rates_count": 0,
        "missing_quantities_count": 0
    }
    
    # Calculate total from line items
    calculated_total = 0.0
    missing_rates = 0
    missing_quantities = 0
    
    for page in data.get('pagewise_line_items', []):
        for item in page.get('bill_items', []):
            amount = item.get('item_amount', 0.0)
            if amount != -1:
                calculated_total += amount
            
            if item.get('item_rate', -1) == -1:
                missing_rates += 1
            if item.get('item_quantity', -1) == -1:
                missing_quantities += 1
    
    validation['calculated_total'] = round(calculated_total, 2)
    validation['missing_rates_count'] = missing_rates
    validation['missing_quantities_count'] = missing_quantities
    
    # Check for duplicates
    duplicates = detect_duplicates(data.get('pagewise_line_items', []))
    validation['duplicate_count'] = len(duplicates)
    
    # Compare with extracted final total
    extracted_total = data.get('final_total', -1)
    if extracted_total != -1:
        validation['has_final_total'] = True
        validation['extracted_total'] = extracted_total
        
        # Calculate match percentage
        if extracted_total > 0:
            discrepancy = abs(calculated_total - extracted_total)
            validation['discrepancy_amount'] = round(discrepancy, 2)
            validation['match_percentage'] = round((1 - discrepancy / extracted_total) * 100, 2)
            validation['has_discrepancy'] = discrepancy > 1.0  # Allow ₹1 tolerance
    
    return validation


def encode_file_to_base64(content: bytes, mime_type: str) -> str:
    """Encode file content to base64 for OpenRouter vision API"""
    base64_content = base64.b64encode(content).decode('utf-8')
    return f"data:{mime_type};base64,{base64_content}"


def extract_json_from_text(text: str) -> Optional[Dict]:
    """Extract JSON from model output (handles markdown code blocks)"""
    # Try direct JSON parse
    try:
        return json.loads(text)
    except:
        pass
    
    # Remove markdown code blocks
    import re
    
    # Try to find JSON in markdown code block
    patterns = [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
        r'(\{.*?\})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                continue
    
    return None


@app.post("/extract-bill-data")
def extract_bill_data(payload: DocumentInput):
    """
    Main endpoint for bill extraction
    Endpoint: POST /extract-bill-data
    """
    url = str(payload.document)

    # Step 1: Fetch document
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True) as client_http:
            resp = client_http.get(url)
            resp.raise_for_status()
            content = resp.content
            headers = resp.headers
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot fetch URL: {e}")
    
    # Step 2: Detect file type
    mime_type, kind = detect_file_type(url, content, headers)
    if kind == "unknown":
        raise HTTPException(status_code=400, detail="Could not determine file type (not PDF or image)")

    # Step 3: Encode file to base64 for OpenRouter
    try:
        base64_data = encode_file_to_base64(content, mime_type)
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to encode file: {e}\n{tb}")

    # Step 4: Call OpenRouter API with Gemini 2.0 Flash
    prompt = f"File type: {kind} (mime: {mime_type})\n\n{ENHANCED_PROMPT}"
    
    try:
        # Prepare OpenRouter request
        openrouter_request = {
            "model": "google/gemini-2.0-flash-exp:free",  # Using free tier
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Make request to OpenRouter
        with httpx.Client(timeout=120.0) as client_http:
            response = client_http.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",  # Optional
                    "X-Title": "Medical Bill Extraction"  # Optional
                },
                json=openrouter_request
            )
            response.raise_for_status()
            openrouter_response = response.json()
            
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"OpenRouter API call failed: {e}\n{tb}")

    # Step 5: Parse response
    try:
        text_out = openrouter_response["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=502, detail=f"Invalid OpenRouter response format: {e}")
    
    parsed_json = extract_json_from_text(text_out)
    
    if parsed_json is None:
        failure_response = {
            "is_success": False,
            "token_usage": {
                "total_tokens": -1,
                "input_tokens": -1,
                "output_tokens": -1
            },
            "data": {
                "pagewise_line_items": [],
                "section_wise_subtotals": [],
                "final_total": -1,
                "total_item_count": 0
            },
            "model_raw_output": text_out[:500]  # First 500 chars for debugging
        }
        raise HTTPException(status_code=502, detail=json.dumps(failure_response))

    # Step 6: Add token usage from OpenRouter response
    if 'usage' in openrouter_response:
        usage = openrouter_response['usage']
        if 'token_usage' in parsed_json:
            parsed_json['token_usage'] = {
                "total_tokens": usage.get('total_tokens', -1),
                "input_tokens": usage.get('prompt_tokens', -1),
                "output_tokens": usage.get('completion_tokens', -1)
            }

    # Step 7: Validate extraction
    if 'data' in parsed_json:
        validation = validate_extraction(parsed_json['data'])
        parsed_json['validation'] = validation
        
        # If discrepancy is too high, mark as failed
        if validation.get('has_discrepancy') and validation.get('match_percentage', 0) < 90:
            parsed_json['is_success'] = False
            parsed_json['warning'] = f"Total mismatch: Calculated={validation['calculated_total']}, Extracted={validation['extracted_total']}"

    return parsed_json


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Medical Bill Extraction API",
        "provider": "OpenRouter",
        "model": "google/gemini-2.0-flash-exp:free",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "ok",
        "provider": "OpenRouter",
        "model": "google/gemini-2.0-flash-exp:free",
        "api_key_configured": bool(OPENROUTER_API_KEY),
        "features": [
            "PDF extraction",
            "Image extraction",
            "Duplicate detection",
            "Validation",
            "Sub-total extraction",
            "Final total extraction"
        ]
    }
