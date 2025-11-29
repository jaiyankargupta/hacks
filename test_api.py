"""
Test script for the Bill Extraction API
Run this to test the API with sample documents
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# Sample test documents (replace with actual URLs from training data)
TEST_DOCUMENTS = [
    "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.pdf",
    "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png",
]

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_extraction(document_url):
    """Test bill extraction"""
    print(f"📄 Testing extraction for: {document_url}")
    
    payload = {"document": document_url}
    response = requests.post(
        f"{BASE_URL}/extract-bill-data",
        json=payload,
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result.get('is_success')}")
        
        if 'data' in result:
            data = result['data']
            print(f"📊 Total Items: {data.get('total_item_count', 0)}")
            print(f"💰 Final Total: ₹{data.get('final_total', -1)}")
            
            if 'validation' in result:
                val = result['validation']
                print(f"🎯 Match Percentage: {val.get('match_percentage', 0)}%")
                print(f"📈 Calculated Total: ₹{val.get('calculated_total', 0)}")
                print(f"🔍 Duplicates Found: {val.get('duplicate_count', 0)}")
        
        # Print first few items
        if 'data' in result and result['data'].get('pagewise_line_items'):
            print("\n📋 Sample Items:")
            for page in result['data']['pagewise_line_items'][:1]:  # First page only
                for item in page.get('bill_items', [])[:3]:  # First 3 items
                    print(f"  - {item['item_name']}: ₹{item['item_amount']}")
        
        print("\n" + "="*60)
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {response.text}")
    
    print("\n" + "="*80 + "\n")

def main():
    """Run all tests"""
    print("🚀 Starting Bill Extraction API Tests\n")
    print("="*80 + "\n")
    
    # Test health
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("Make sure the server is running: uvicorn app:app --reload")
        return
    
    # Test extraction
    for doc_url in TEST_DOCUMENTS:
        try:
            test_extraction(doc_url)
        except Exception as e:
            print(f"❌ Extraction failed for {doc_url}: {e}\n")

if __name__ == "__main__":
    main()
