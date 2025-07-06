#!/usr/bin/env python3
"""
Hugging Face API Diagnostics Script
Helps troubleshoot common Hugging Face API issues
"""

import os
import sys
import requests
from typing import Dict, Any, Optional

def check_hf_installation() -> bool:
    """Check if huggingface_hub is installed"""
    try:
        import huggingface_hub
        print(f"✅ Hugging Face Hub installed: {huggingface_hub.__version__}")
        return True
    except ImportError:
        print("❌ Hugging Face Hub not installed")
        print("💡 Install with: pip install huggingface_hub")
        return False

def check_token_format(token: str) -> bool:
    """Check if token has correct format"""
    if not token:
        print("❌ No token provided")
        return False
    
    if not token.startswith('hf_'):
        print("❌ Invalid token format - should start with 'hf_'")
        return False
    
    if len(token) < 10:
        print("❌ Token seems too short")
        return False
    
    print("✅ Token format looks correct")
    return True

def test_token_validation(token: str) -> Dict[str, Any]:
    """Test token with Hugging Face API"""
    try:
        from huggingface_hub import InferenceClient
        
        print("🔧 Testing token validation...")
        client = InferenceClient(token=token)
        
        # Test with a simple model
        print("🤖 Testing with gpt2 model...")
        response = client.text_generation(
            "Hello",
            model="gpt2",
            max_new_tokens=5,
            return_full_text=False
        )
        
        print("✅ Token validation successful!")
        return {"success": True, "response": response}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Token validation failed: {error_msg}")
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            return {
                "success": False, 
                "error": "401 Unauthorized",
                "suggestions": [
                    "Token is invalid or expired",
                    "Get a new token from https://huggingface.co/settings/tokens",
                    "Check if your account is active"
                ]
            }
        elif "403" in error_msg or "Forbidden" in error_msg:
            return {
                "success": False,
                "error": "403 Forbidden", 
                "suggestions": [
                    "Token doesn't have required permissions",
                    "Add 'read' access for inference",
                    "Check if model requires special access"
                ]
            }
        elif "429" in error_msg or "Rate limit" in error_msg:
            return {
                "success": False,
                "error": "429 Rate Limited",
                "suggestions": [
                    "Too many requests",
                    "Wait a moment and try again",
                    "Consider upgrading to Pro account"
                ]
            }
        else:
            return {
                "success": False,
                "error": "Unknown error",
                "suggestions": [
                    "Check your internet connection",
                    "Verify Hugging Face service status",
                    "Try again later"
                ]
            }

def check_hf_status() -> bool:
    """Check Hugging Face service status"""
    try:
        print("🌐 Checking Hugging Face service status...")
        response = requests.get("https://huggingface.co", timeout=10)
        if response.status_code == 200:
            print("✅ Hugging Face website is accessible")
            return True
        else:
            print(f"⚠️ Hugging Face website returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach Hugging Face: {str(e)}")
        return False

def test_model_access(token: str, model: str = "gpt2") -> Dict[str, Any]:
    """Test access to specific model"""
    try:
        from huggingface_hub import InferenceClient
        
        print(f"🔍 Testing access to model: {model}")
        client = InferenceClient(token=token)
        
        response = client.text_generation(
            "Test message",
            model=model,
            max_new_tokens=10,
            return_full_text=False
        )
        
        print(f"✅ Successfully accessed {model}")
        return {"success": True, "model": model}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to access {model}: {error_msg}")
        return {"success": False, "model": model, "error": error_msg}

def run_diagnostics(token: Optional[str] = None) -> None:
    """Run comprehensive Hugging Face diagnostics"""
    print("🔍 Hugging Face API Diagnostics")
    print("=" * 50)
    
    # Check installation
    if not check_hf_installation():
        return
    
    # Check service status
    if not check_hf_status():
        print("💡 Hugging Face service may be down. Check: https://status.huggingface.co")
        return
    
    # Get token
    if not token:
        token = os.getenv('HF_TOKEN')
        if not token:
            print("❌ No HF_TOKEN found in environment")
            print("💡 Set your token: export HF_TOKEN='your_token_here'")
            return
    
    # Check token format
    if not check_token_format(token):
        return
    
    # Test token validation
    validation_result = test_token_validation(token)
    
    if validation_result["success"]:
        print("\n🎉 All diagnostics passed! Your Hugging Face setup is working correctly.")
        
        # Test additional models
        print("\n🔍 Testing additional models...")
        models_to_test = ["gpt2", "microsoft/DialoGPT-medium"]
        
        for model in models_to_test:
            test_model_access(token, model)
            
    else:
        print(f"\n❌ Diagnostics failed: {validation_result['error']}")
        print("\n💡 Suggested solutions:")
        for suggestion in validation_result.get('suggestions', []):
            print(f"   • {suggestion}")
        
        print("\n🔗 Helpful links:")
        print("   • Token settings: https://huggingface.co/settings/tokens")
        print("   • Community forum: https://discuss.huggingface.co")
        print("   • Service status: https://status.huggingface.co")

if __name__ == "__main__":
    # Get token from command line argument or environment
    token = sys.argv[1] if len(sys.argv) > 1 else None
    run_diagnostics(token) 