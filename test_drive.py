"""
Helper script to test API with Google Drive files
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def convert_drive_link(drive_url):
    """Convert Google Drive share link to direct download link"""
    if "drive.google.com/file/d/" in drive_url:
        # Extract file ID
        file_id = drive_url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    elif "drive.google.com/uc" in drive_url:
        # Already a direct link
        return drive_url
    else:
        print(f"⚠️  Warning: URL doesn't look like a Google Drive link")
        return drive_url

def test_extraction(document_url):
    """Test bill extraction with given URL"""
    # Convert if it's a Drive link
    direct_url = convert_drive_link(document_url)
    
    print(f"\n{'='*80}")
    print(f"🧪 Testing Bill Extraction")
    print(f"{'='*80}\n")
    print(f"📄 Original URL: {document_url}")
    if direct_url != document_url:
        print(f"🔗 Direct URL:   {direct_url}")
    print()
    
    payload = {"document": direct_url}
    
    print("⏳ Sending request to API...")
    try:
        response = requests.post(
            f"{BASE_URL}/extract-bill-data",
            json=payload,
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            
            # Print summary
            print("✅ SUCCESS!\n")
            print(f"{'='*80}")
            print("📋 EXTRACTION SUMMARY")
            print(f"{'='*80}\n")
            
            if 'data' in result:
                data = result['data']
                print(f"📦 Total Items: {data.get('total_item_count', 0)}")
                print(f"💰 Final Total: ₹{data.get('final_total', -1)}")
                
                if 'section_wise_subtotals' in data and data['section_wise_subtotals']:
                    print(f"\n📊 Section Subtotals:")
                    for section in data['section_wise_subtotals']:
                        print(f"   - {section['section_name']}: ₹{section['subtotal']} ({section['item_count']} items)")
            
            if 'validation' in result:
                val = result['validation']
                print(f"\n🎯 Validation:")
                print(f"   - Match Percentage: {val.get('match_percentage', 0)}%")
                print(f"   - Calculated Total: ₹{val.get('calculated_total', 0)}")
                print(f"   - Extracted Total:  ₹{val.get('extracted_total', 0)}")
                print(f"   - Discrepancy: ₹{val.get('discrepancy_amount', 0)}")
                print(f"   - Duplicates Found: {val.get('duplicate_count', 0)}")
            
            if 'token_usage' in result:
                tokens = result['token_usage']
                print(f"\n💡 Token Usage:")
                print(f"   - Total: {tokens.get('total_tokens', -1)}")
                print(f"   - Input: {tokens.get('input_tokens', -1)}")
                print(f"   - Output: {tokens.get('output_tokens', -1)}")
            
            # Print first few items
            if 'data' in result and result['data'].get('pagewise_line_items'):
                print(f"\n📝 Sample Line Items (first 5):")
                item_count = 0
                for page in result['data']['pagewise_line_items']:
                    for item in page.get('bill_items', []):
                        if item_count >= 5:
                            break
                        print(f"   {item_count+1}. {item['item_name']}: ₹{item['item_amount']} (qty: {item['item_quantity']}, rate: ₹{item['item_rate']})")
                        item_count += 1
                    if item_count >= 5:
                        break
            
            print(f"\n{'='*80}")
            print("📄 FULL JSON RESPONSE")
            print(f"{'='*80}\n")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ ERROR: {response.status_code}\n")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120 seconds)")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Google Drive Bill Extraction Tester\n")
    
    if len(sys.argv) > 1:
        # URL provided as argument
        document_url = sys.argv[1]
    else:
        # Prompt for URL
        print("Please provide a Google Drive link to a bill PDF/image:")
        print("Example: https://drive.google.com/file/d/1ABC123.../view?usp=sharing\n")
        document_url = input("Enter URL: ").strip()
    
    if not document_url:
        print("❌ No URL provided!")
        print("\nUsage:")
        print("  python test_drive.py <google_drive_url>")
        print("\nOr run without arguments to enter URL interactively")
        return
    
    test_extraction(document_url)

if __name__ == "__main__":
    main()
