import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_token_format(token):
    """Verify the token format"""
    print("=== Token Format Verification ===")
    print(f"Token length: {len(token)} characters")
    print(f"Token starts with 'hf_': {token.startswith('hf_')}")
    print(f"Token preview: {token[:10]}...{token[-5:]}")
    
    if not token.startswith('hf_'):
        print("❌ Token should start with 'hf_'")
        return False
    
    if len(token) < 20:
        print("❌ Token seems too short")
        return False
    
    print("✅ Token format looks correct")
    return True

def test_basic_connectivity():
    """Test basic connectivity to Hugging Face"""
    print("\n=== Basic Connectivity Test ===")
    try:
        response = requests.get("https://huggingface.co/api/whoami", timeout=10)
        print(f"Status without auth: {response.status_code}")
        print("✅ Can reach Hugging Face API")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Hugging Face: {e}")
        return False

def test_token_again(token):
    """Test the token again with more details"""
    print(f"\n=== Testing Token: {token[:10]}... ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Success! User: {user_info}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Get token from environment variable
    token = os.getenv('HUGGINGFACE_API_KEY')
    
    if not token:
        print("❌ No Hugging Face API key found in environment")
        print("Please set HUGGINGFACE_API_KEY in your .env file")
        exit(1)
    
    print("Hugging Face Token Verification")
    print("=" * 40)
    
    # Verify format
    if verify_token_format(token):
        # Test connectivity
        if test_basic_connectivity():
            # Test token
            test_token_again(token)
    
    print("\n" + "=" * 40)
    print("TROUBLESHOOTING TIPS:")
    print("1. Make sure you're logged into Hugging Face")
    print("2. Go to https://huggingface.co/settings/tokens")
    print("3. Create a new token with 'Read' permissions")
    print("4. Copy the complete token (should start with 'hf_')")
    print("5. Make sure there are no extra spaces or characters") 