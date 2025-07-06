"""
Configuration file for ResumeAI Helper
Handles Hugging Face API issues and provides fallback options
"""

import os
from typing import List, Dict, Any

# Hugging Face API Status
HF_API_ISSUES = {
    "widespread_401_error": True,  # Known widespread issue since June 2025
    "widespread_404_error": True,  # Known widespread issue affecting many users
    "recommended_fallback": "ollama",  # Recommended fallback when HF fails
}

# Default models for different providers
DEFAULT_MODELS = {
    "huggingface": [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "meta-llama/Llama-2-7b-chat-hf", 
        "microsoft/DialoGPT-medium",
        "gpt2",
        "tiiuae/falcon-7b-instruct"
    ],
    "ollama": [
        "llama3.1",
        "mistral", 
        "gemma3:12b",
        "llama3.2",
        "codellama"
    ]
}

# Error messages and solutions
ERROR_MESSAGES = {
    "hf_401": {
        "title": "❌ 401 Unauthorized Error (WIDESPREAD ISSUE)",
        "description": "This is a known issue affecting many users since June 2025. Even newly generated tokens are failing.",
        "solutions": [
            "Use Ollama instead - This is the most reliable solution",
            "Check token format - Must start with `hf_`",
            "Verify token validity - Get a new token from Hugging Face",
            "Check account status - Ensure your account is active",
            "Token permissions - Make sure token has 'read' access",
            "Contact support - Email website@huggingface.co"
        ]
    },
    "hf_404": {
        "title": "❌ 404 Not Found Error (WIDESPREAD ISSUE)", 
        "description": "This is a widespread issue affecting many users due to backend changes at Hugging Face.",
        "solutions": [
            "Try different models - Some models still work",
            "Use Ollama (local) instead of Hugging Face",
            "Check Hugging Face status page",
            "Visit community forum for updates",
            "Wait for Hugging Face to resolve the issue"
        ]
    },
    "hf_403": {
        "title": "❌ 403 Forbidden Error",
        "description": "Your token doesn't have the required permissions.",
        "solutions": [
            "Update token permissions - Add 'read' access for inference",
            "Check model access - Some models require special access", 
            "Verify account type - Free accounts have usage limits"
        ]
    },
    "hf_429": {
        "title": "❌ 429 Rate Limited",
        "description": "Too many requests to Hugging Face API.",
        "solutions": [
            "Wait and retry - Rate limits reset automatically",
            "Upgrade account - Pro accounts have higher limits",
            "Reduce request frequency - Space out your API calls"
        ]
    },
    "hf_500": {
        "title": "❌ 500 Server Error", 
        "description": "Hugging Face service temporarily unavailable.",
        "solutions": [
            "Try again later - Temporary service issue",
            "Check Hugging Face status page",
            "Use different model - Some models may be temporarily unavailable"
        ]
    }
}

# File upload settings
FILE_UPLOAD_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB limit for Hugging Face Spaces
    "allowed_extensions": ["pdf", "docx", "txt"],
    "temp_dir": "/tmp/streamlit",  # Use temp directory for file uploads
}

# Streamlit configuration for Hugging Face Spaces
STREAMLIT_CONFIG = {
    "server_port": 7860,
    "server_address": "0.0.0.0", 
    "server_headless": True,
    "server_enable_cors": False,
    "server_enable_xsrf_protection": False,
    "server_file_watcher_type": "none",
    "browser_gather_usage_stats": False,
    "python_unbuffered": True,
    "hf_home": "/tmp/huggingface"
}

def get_error_info(error_type: str) -> Dict[str, Any]:
    """Get error information and solutions."""
    return ERROR_MESSAGES.get(error_type, {
        "title": "❌ Unknown Error",
        "description": "An unexpected error occurred.",
        "solutions": ["Please try again later", "Check your internet connection"]
    })

def should_use_fallback() -> bool:
    """Determine if we should use fallback due to widespread HF issues."""
    return HF_API_ISSUES.get("widespread_401_error", False) or \
           HF_API_ISSUES.get("widespread_404_error", False)

def get_recommended_provider() -> str:
    """Get recommended AI provider based on current issues."""
    if should_use_fallback():
        return HF_API_ISSUES.get("recommended_fallback", "ollama")
    return "huggingface" 