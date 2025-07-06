#!/usr/bin/env python3
"""
Simple test script to check Hugging Face API connectivity
"""

import os
import requests
import json
from huggingface_hub import InferenceClient

def test_hf_api():
    """Test Hugging Face API with different approaches"""
    
    print("🔍 Testing Hugging Face API Connectivity...")
    print("=" * 50)
    
    # Get token from environment or user input
    token = os.getenv('HF_TOKEN')
    if not token:
        token = input("Enter your Hugging Face API token (starts with 'hf_'): ").strip()
    
    if not token:
        print("❌ No token provided")
        return
    
    if not token.startswith('hf_'):
        print("❌ Invalid token format. Token should start with 'hf_'")
        return
    
    print(f"✅ Token format looks correct: {token[:10]}...")
    
    # Test 1: Direct API call
    print("\n1️⃣ Testing direct API call...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try a simple model first
    test_models = [
        "gpt2",
        "microsoft/DialoGPT-small",
        "distilbert-base-uncased"
    ]
    
    for model in test_models:
        print(f"   Testing model: {model}")
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            
            # Simple text generation test
            payload = {"inputs": "Hello world"}
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success with {model}")
                result = response.json()
                print(f"   Response: {str(result)[:100]}...")
                break
            elif response.status_code == 401:
                print(f"   ❌ 401 Unauthorized - Invalid token")
                return
            elif response.status_code == 403:
                print(f"   ❌ 403 Forbidden - Token doesn't have permissions")
                return
            elif response.status_code == 404:
                print(f"   ⚠️ 404 Not Found - Model not available")
                continue
            elif response.status_code == 429:
                print(f"   ⚠️ 429 Rate Limited - Too many requests")
                continue
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⚠️ Timeout for {model}")
            continue
        except Exception as e:
            print(f"   ❌ Exception for {model}: {str(e)}")
            continue
    
    # Test 2: Using InferenceClient
    print("\n2️⃣ Testing InferenceClient...")
    try:
        client = InferenceClient(token=token)
        print("   ✅ InferenceClient created successfully")
        
        # Test with a simple model
        try:
            response = client.text_generation(
                "Hello",
                model="gpt2",
                max_new_tokens=5,
                return_full_text=False
            )
            print(f"   ✅ InferenceClient test successful: {response}")
        except Exception as e:
            print(f"   ❌ InferenceClient test failed: {str(e)}")
            
    except Exception as e:
        print(f"   ❌ Failed to create InferenceClient: {str(e)}")
    
    # Test 3: Check token permissions
    print("\n3️⃣ Checking token permissions...")
    try:
        url = "https://huggingface.co/api/whoami"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ Token is valid for user: {user_info.get('name', 'Unknown')}")
            print(f"   📧 Email: {user_info.get('email', 'Not shown')}")
        else:
            print(f"   ❌ Failed to get user info: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking permissions: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    print("• If you got 401 errors: Check your token at https://huggingface.co/settings/tokens")
    print("• If you got 403 errors: Make sure your token has 'read' permissions")
    print("• If you got 404 errors: This is a known issue - try different models or use Ollama")
    print("• If you got 429 errors: Wait a moment and try again")
    print("• If all tests failed: Check your internet connection")

if __name__ == "__main__":
    test_hf_api() 