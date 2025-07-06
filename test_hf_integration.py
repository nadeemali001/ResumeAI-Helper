#!/usr/bin/env python3
"""
Test script for Hugging Face integration
"""

import os
from utils import get_hf_client, hf_text_generation, HF_AVAILABLE

def test_hf_integration():
    """Test Hugging Face integration"""
    print("Testing Hugging Face Integration...")
    print(f"HF_AVAILABLE: {HF_AVAILABLE}")
    
    if not HF_AVAILABLE:
        print("❌ Hugging Face Hub not available")
        return False
    
    # Get token from environment
    token = os.getenv('HF_TOKEN')
    if not token:
        print("❌ HF_TOKEN not found in environment")
        print("💡 Set your token: export HF_TOKEN='your_token_here'")
        return False
    
    try:
        # Test client creation
        print("🔧 Testing client creation...")
        client = get_hf_client(token)
        if not client:
            print("❌ Failed to create HF client")
            return False
        print("✅ HF client created successfully")
        
        # Test simple text generation
        print("🤖 Testing text generation...")
        prompt = "Hello, how are you?"
        response = hf_text_generation(client, "gpt2", prompt, max_tokens=50)
        
        if response:
            print(f"✅ Text generation successful: {response[:100]}...")
            return True
        else:
            print("❌ Text generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_hf_integration()
    if success:
        print("\n🎉 Hugging Face integration test passed!")
    else:
        print("\n💥 Hugging Face integration test failed!") 