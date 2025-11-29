"""
Test the Bill Extraction API with local training samples
"""

import requests
import json
import os
from pathlib import Path

# API endpoint
BASE_URL = "http://localhost:8000"

# Training samples directory
SAMPLES_DIR = "TRAINING_SAMPLES"

def test_with_local_file(file_path):
    """Test API with a local file by uploading it"""
    print(f"\n{'='*80}")
    print(f"Testing: {file_path}")
    print(f"{'='*80}\n")
    
    # For now, we need to upload files to a public URL
    # Let's use a simple approach: convert to base64 and modify the API
    # Or we can use a local file server
    
    # For this test, let's just show the file info
    file_size = os.path.getsize(file_path)
    print(f"📄 File: {os.path.basename(file_path)}")
    print(f"📊 Size: {file_size / 1024:.2f} KB")
    print(f"📁 Path: {file_path}")
    
    return file_path

def list_training_samples():
    """List all training samples"""
    samples_path = Path(SAMPLES_DIR)
    if not samples_path.exists():
        print(f"❌ Directory {SAMPLES_DIR} not found!")
        print("Please extract TRAINING_SAMPLES.zip first")
        return []
    
    pdf_files = sorted(samples_path.glob("*.pdf"))
    print(f"\n📚 Found {len(pdf_files)} training samples:\n")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        size_kb = pdf_file.stat().st_size / 1024
        print(f"{i:2d}. {pdf_file.name:30s} ({size_kb:6.2f} KB)")
    
    return pdf_files

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("Make sure the server is running: uvicorn app:app --reload")
        return False

def main():
    """Main test function"""
    print("🚀 Bill Extraction API - Training Samples Test\n")
    print("="*80 + "\n")
    
    # Test health
    if not test_health():
        return
    
    # List samples
    pdf_files = list_training_samples()
    
    if not pdf_files:
        return
    
    print("\n" + "="*80)
    print("📝 NEXT STEPS:")
    print("="*80)
    print("\nTo test with these files, you have two options:\n")
    print("1. Upload files to a public URL (e.g., GitHub, cloud storage)")
    print("2. Modify the API to accept file uploads directly\n")
    print("For now, the files are extracted and ready in: TRAINING_SAMPLES/")
    print("\nTo test with a public URL:")
    print('  curl -X POST "http://localhost:8000/extract-bill-data" \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"document": "YOUR_PUBLIC_URL_HERE"}\'')
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
