#!/usr/bin/env python3
"""
Simple test script to verify Ollama is working correctly
"""

import ollama
import json

def test_ollama():
    """Test Ollama with a simple prompt"""
    
    print("🔍 Testing Ollama Connection...")
    print("=" * 50)
    
    try:
        # Test 1: List models
        print("1️⃣ Checking available models...")
        models_response = ollama.list()
        print(f"   ✅ Found {len(models_response.models)} models:")
        for model in models_response.models:
            print(f"   • {model.model}")
        
        # Test 2: Simple chat
        print("\n2️⃣ Testing simple chat...")
        response = ollama.chat(
            model="llama3.1",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, Ollama is working!' in one sentence."
                }
            ]
        )
        
        print(f"   ✅ Response: {response['message']['content']}")
        
        # Test 3: JSON response test (like our app uses)
        print("\n3️⃣ Testing JSON response capability...")
        response = ollama.chat(
            model="llama3.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": "Return this JSON: {\"test\": \"success\", \"message\": \"Ollama is working perfectly\"}"
                }
            ]
        )
        
        print(f"   ✅ Response: {response['message']['content']}")
        
        # Test 4: Resume analysis test
        print("\n4️⃣ Testing resume analysis capability...")
        test_prompt = """
        Analyze this simple resume and job description:
        
        Resume: Software engineer with 3 years experience in Python and JavaScript.
        
        Job Description: Looking for a Python developer with 2+ years experience.
        
        Return a simple JSON with: {"score": 85, "summary": "Good match"}
        """
        
        response = ollama.chat(
            model="llama3.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert HR professional. Provide analysis in JSON format."
                },
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        )
        
        print(f"   ✅ Analysis response: {response['message']['content'][:100]}...")
        
        print("\n" + "=" * 50)
        print("🎉 All Ollama tests passed! Your app should work perfectly.")
        print("💡 You can now use the Streamlit app with Ollama models.")
        
    except Exception as e:
        print(f"❌ Ollama test failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Check available models: ollama list")
        print("3. Pull a model if needed: ollama pull llama3.1")

if __name__ == "__main__":
    test_ollama() 