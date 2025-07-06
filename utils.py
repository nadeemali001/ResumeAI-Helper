import fitz  # PyMuPDF
from docx import Document
import streamlit as st
from typing import Optional, Dict, Any
import ollama
import os
import json
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from collections import Counter
import numpy as np
import re

# Hugging Face imports
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


def get_hf_client(api_token: Optional[str] = None) -> Optional[Any]:
    """
    Get Hugging Face InferenceClient instance.
    
    Args:
        api_token: Hugging Face API token. If None, tries to get from environment.
        
    Returns:
        InferenceClient instance or None if not available
    """
    if not HF_AVAILABLE:
        st.error("Hugging Face Hub not installed. Run: pip install huggingface_hub")
        return None
    
    try:
        # Try to get token from parameter, then environment, then secrets
        token = api_token or os.getenv('HF_TOKEN') or st.secrets.get('HF_TOKEN', None)
        
        if not token:
            st.error("Hugging Face API token not found. Please provide a valid token.")
            return None
        
        # Validate token format
        if not token.startswith('hf_'):
            st.error("Invalid Hugging Face token format. Token should start with 'hf_'")
            return None
            
        client = InferenceClient(token=token)
        
        # Test the token with a simple request
        try:
            # Try a simple test to validate the token
            test_response = client.text_generation(
                "Hello",
                model="gpt2",
                max_new_tokens=5,
                return_full_text=False
            )
            return client
        except Exception as auth_error:
            error_msg = str(auth_error)
            if "401" in error_msg or "Unauthorized" in error_msg:
                st.error("❌ 401 Unauthorized: Invalid Hugging Face API token. Please check your token and try again.")
                st.info("💡 Get a new token from: https://huggingface.co/settings/tokens")
            elif "403" in error_msg or "Forbidden" in error_msg:
                st.error("❌ 403 Forbidden: Your token doesn't have the required permissions.")
                st.info("💡 Make sure your token has 'read' permissions for inference.")
            elif "404" in error_msg or "Not Found" in error_msg:
                st.error("❌ 404 Not Found: Model not available or API endpoint issue.")
                st.warning("⚠️ This is a known issue affecting many users recently.")
                st.info("💡 **Temporary Solutions:**")
                st.info("• Try different models (some models still work)")
                st.info("• Use Ollama (local) instead of Hugging Face")
                st.info("• Check [Hugging Face status](https://status.huggingface.co)")
                st.info("• Visit [community forum](https://discuss.huggingface.co) for updates")
            elif "429" in error_msg or "Rate limit" in error_msg:
                st.error("❌ 429 Rate Limited: Too many requests.")
                st.info("💡 Wait a moment and try again, or upgrade to Pro account.")
            elif "500" in error_msg or "Internal Server Error" in error_msg:
                st.error("❌ 500 Server Error: Hugging Face service temporarily unavailable.")
                st.info("💡 Please try again later.")
            else:
                st.error(f"❌ Hugging Face API error: {error_msg}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error initializing Hugging Face client: {str(e)}")
        st.info("💡 Common solutions:")
        st.info("• Check your internet connection")
        st.info("• Verify your API token is correct")
        st.info("• Ensure your token has the right permissions")
        return None


def hf_chat_completion(client: Any, model: str, messages: list, max_tokens: int = 1000) -> Optional[str]:
    """
    Generate chat completion using Hugging Face Inference API.
    
    Args:
        client: Hugging Face InferenceClient instance
        model: Model name (e.g., "mistralai/Mistral-7B-Instruct")
        messages: List of message dictionaries with 'role' and 'content'
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        Generated text or None if failed
    """
    if not client:
        return None
    
    try:
        # Convert messages to the format expected by HF
        formatted_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                # For system messages, prepend to user message or handle separately
                continue
            elif msg['role'] == 'user':
                formatted_messages.append(f"<s>[INST] {msg['content']} [/INST]")
            elif msg['role'] == 'assistant':
                formatted_messages.append(f"{msg['content']} </s>")
        
        # Join messages
        prompt = " ".join(formatted_messages)
        
        # Generate response
        response = client.text_generation(
            prompt,
            model=model,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )
        
        return response.strip()
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            st.error("❌ 401 Unauthorized: Invalid Hugging Face API token")
            st.info("💡 Please check your token and ensure it has the correct permissions")
        elif "403" in error_msg or "Forbidden" in error_msg:
            st.error("❌ 403 Forbidden: Token doesn't have required permissions")
            st.info("💡 Make sure your token has 'read' permissions for inference")
        elif "404" in error_msg or "Not Found" in error_msg:
            st.error("❌ 404 Not Found: Model not available or API endpoint issue")
            st.warning("⚠️ This is a known issue affecting many users recently")
            st.info("💡 **Temporary Solutions:**")
            st.info("• Try different models (some models still work)")
            st.info("• Use Ollama (local) instead of Hugging Face")
            st.info("• Check [Hugging Face status](https://status.huggingface.co)")
            st.info("• Visit [community forum](https://discuss.huggingface.co) for updates")
        elif "429" in error_msg or "Rate limit" in error_msg:
            st.error("❌ 429 Rate Limited: Too many requests")
            st.info("💡 Please wait a moment and try again")
        elif "500" in error_msg or "Internal Server Error" in error_msg:
            st.error("❌ 500 Server Error: Hugging Face service temporarily unavailable")
            st.info("💡 Please try again later")
        else:
            st.error(f"❌ Hugging Face API error: {error_msg}")
        return None


def hf_text_generation(client: Any, model: str, prompt: str, max_tokens: int = 1000) -> Optional[str]:
    """
    Generate text using Hugging Face Inference API.
    
    Args:
        client: Hugging Face InferenceClient instance
        model: Model name
        prompt: Input prompt
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        Generated text or None if failed
    """
    if not client:
        return None
    
    try:
        response = client.text_generation(
            prompt,
            model=model,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )
        
        return response.strip()
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            st.error("❌ 401 Unauthorized: Invalid Hugging Face API token")
            st.info("💡 Please check your token and ensure it has the correct permissions")
        elif "403" in error_msg or "Forbidden" in error_msg:
            st.error("❌ 403 Forbidden: Token doesn't have required permissions")
            st.info("💡 Make sure your token has 'read' permissions for inference")
        elif "404" in error_msg or "Not Found" in error_msg:
            st.error("❌ 404 Not Found: Model not available or API endpoint issue")
            st.warning("⚠️ This is a known issue affecting many users recently")
            st.info("💡 **Temporary Solutions:**")
            st.info("• Try different models (some models still work)")
            st.info("• Use Ollama (local) instead of Hugging Face")
            st.info("• Check [Hugging Face status](https://status.huggingface.co)")
            st.info("• Visit [community forum](https://discuss.huggingface.co) for updates")
        elif "429" in error_msg or "Rate limit" in error_msg:
            st.error("❌ 429 Rate Limited: Too many requests")
            st.info("💡 Please wait a moment and try again")
        elif "500" in error_msg or "Internal Server Error" in error_msg:
            st.error("❌ 500 Server Error: Hugging Face service temporarily unavailable")
            st.info("💡 Please try again later")
        else:
            st.error(f"❌ Hugging Face API error: {error_msg}")
        return None


def extract_text_from_file(file) -> Optional[str]:
    """
    Extract text from uploaded file (PDF or DOCX).
    
    Args:
        file: Streamlit uploaded file object
        
    Returns:
        str: Extracted text from the file, or None if extraction fails
    """
    try:
        if file is None:
            return None
            
        file_extension = file.name.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return _extract_text_from_pdf(file)
        elif file_extension == 'docx':
            return _extract_text_from_docx(file)
        elif file_extension == 'txt':
            return _extract_text_from_txt(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text from {file.name}: {str(e)}")
        return None


def _extract_text_from_pdf(file) -> str:
    """Extract text from PDF file using PyMuPDF."""
    try:
        # Read the PDF file
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        
        # Extract text from each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()  # type: ignore
            
        pdf_document.close()
        return text.strip()
        
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")


def _extract_text_from_docx(file) -> str:
    """Extract text from DOCX file using python-docx."""
    try:
        # Read the DOCX file
        doc = Document(file)
        text = ""
        
        # Extract text from each paragraph
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            
        return text.strip()
        
    except Exception as e:
        raise Exception(f"DOCX extraction failed: {str(e)}")


def _extract_text_from_txt(file) -> str:
    """Extract text from TXT file."""
    try:
        # Reset file pointer to beginning
        file.seek(0)
        text = file.read().decode('utf-8')
        return text.strip()
        
    except Exception as e:
        raise Exception(f"TXT extraction failed: {str(e)}")


def get_file_info(file) -> dict:
    """
    Get basic information about the uploaded file.
    
    Args:
        file: Streamlit uploaded file object
        
    Returns:
        dict: File information including name, size, and type
    """
    if file is None:
        return {}
        
    return {
        'name': file.name,
        'size': file.size,
        'type': file.type,
        'extension': file.name.lower().split('.')[-1] if '.' in file.name else 'unknown'
    }


def validate_file_type(file, allowed_extensions=['pdf', 'docx', 'txt']) -> bool:
    """
    Validate if the uploaded file has an allowed extension.
    
    Args:
        file: Streamlit uploaded file object
        allowed_extensions: List of allowed file extensions
        
    Returns:
        bool: True if file type is allowed, False otherwise
    """
    if file is None:
        return False
        
    file_extension = file.name.lower().split('.')[-1]
    return file_extension in allowed_extensions


def analyze_resume_vs_jd(resume_text: str, jd_text: str, model_name: str = "llama3.1", use_hf: bool = False, hf_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze resume against job description using AI model (Ollama or Hugging Face) with detailed analysis.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        model_name: Name of the model to use
        use_hf: Whether to use Hugging Face API instead of Ollama
        hf_token: Hugging Face API token (if using HF)
        
    Returns:
        dict: Detailed analysis results with comprehensive feedback
    """
    try:
        # Create the detailed prompt for analysis
        prompt = f"""
        Given this resume and job description, analyze them and return a detailed assessment.
        
        Resume:
        {resume_text}
        
        Job Description:
        {jd_text}
        
        Please provide your analysis in the following JSON format:
        {{
            "score": <overall match score between 0-100>,
            "skills_match": <skills match percentage between 0-100>,
            "missing_keywords": ["<keyword 1>", "<keyword 2>", "<keyword 3>", "<keyword 4>", "<keyword 5>"],
            "found_skills": ["<skill 1>", "<skill 2>", "<skill 3>", "<skill 4>", "<skill 5>"],
            "required_skills_count": <total number of required skills identified>,
            "found_skills_count": <number of required skills found in resume>,
            "missing_skills_count": <number of required skills missing>,
            "additional_skills": ["<bonus skill 1>", "<bonus skill 2>", "<bonus skill 3>"],
            "formatting_issues": ["<issue 1>", "<issue 2>", "<issue 3>"],
            "tone_grammar": "<evaluation of tone and grammar - 1-2 sentences>",
            "summary": "<2-line summary of the overall assessment>",
            "improvements": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>", "<suggestion 4>", "<suggestion 5>"]
        }}
        
        Analysis guidelines:
        1. Overall match score: Consider skills, experience, and alignment with job requirements
        2. Skills match: Percentage of required skills found in resume
        3. Missing keywords: 5-7 important terms from job description not found in resume
        4. Found skills: 5-7 key skills from job description that ARE present in resume
        5. Required skills count: Total number of essential skills identified in job description
        6. Found skills count: Number of those required skills found in resume
        7. Missing skills count: Number of required skills missing from resume
        8. Additional skills: 3-5 bonus skills in resume that weren't required but are valuable
        9. Formatting issues: Problems with structure, bullet points, fonts, spacing, etc.
        10. Tone and grammar: Professional language, spelling, sentence structure
        11. Summary: Concise 2-line overview of strengths and weaknesses
        12. Improvements: 3-5 specific, actionable suggestions to enhance the resume
        
        Only respond with valid JSON. Do not include any other text or explanations outside the JSON structure.
        """
        
        # Choose API based on use_hf parameter
        if use_hf and HF_AVAILABLE:
            # Use Hugging Face API
            hf_client = get_hf_client(hf_token)
            if not hf_client:
                raise Exception("Hugging Face client not available. Please check your API token.")
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert HR professional and resume analyzer with deep knowledge of recruitment best practices. Provide comprehensive, accurate analysis in the exact JSON format requested. Focus on actionable insights and specific recommendations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response_content = hf_chat_completion(hf_client, model_name, messages, max_tokens=2000)
            if not response_content:
                raise Exception("Failed to get response from Hugging Face API")
        else:
            # Use Ollama API
            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR professional and resume analyzer with deep knowledge of recruitment best practices. Provide comprehensive, accurate analysis in the exact JSON format requested. Focus on actionable insights and specific recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            response_content = response['message']['content'].strip()
        
        # Extract the response content
        response_content = response['message']['content'].strip()
        
        # Parse JSON response
        try:
            # Try to extract JSON from the response (in case there's extra text)
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                analysis_result = json.loads(json_str)
            else:
                analysis_result = json.loads(response_content)
                
        except json.JSONDecodeError as e:
            # Fallback: create a structured response from the text
            st.warning("Could not parse AI response as JSON. Using fallback analysis.")
            analysis_result = {
                "score": 75,
                "skills_match": 70,
                "missing_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
                "formatting_issues": ["Review formatting manually"],
                "tone_grammar": "Analysis completed but response format was unexpected.",
                "summary": "Analysis completed but response format was unexpected. Please review the AI response manually for detailed feedback.",
                "improvements": ["Review the AI response manually for detailed feedback."]
            }
        
        # Validate and ensure all required keys exist
        required_keys = ['score', 'skills_match', 'missing_keywords', 'found_skills', 'required_skills_count', 'found_skills_count', 'missing_skills_count', 'additional_skills', 'formatting_issues', 'tone_grammar', 'summary', 'improvements']
        for key in required_keys:
            if key not in analysis_result:
                if key == 'score':
                    analysis_result[key] = 75
                elif key == 'skills_match':
                    analysis_result[key] = 70
                elif key == 'missing_keywords':
                    analysis_result[key] = ["keyword1", "keyword2", "keyword3"]
                elif key == 'found_skills':
                    analysis_result[key] = ["skill1", "skill2", "skill3"]
                elif key == 'required_skills_count':
                    analysis_result[key] = 8
                elif key == 'found_skills_count':
                    analysis_result[key] = 5
                elif key == 'missing_skills_count':
                    analysis_result[key] = 3
                elif key == 'additional_skills':
                    analysis_result[key] = ["bonus1", "bonus2", "bonus3"]
                elif key == 'formatting_issues':
                    analysis_result[key] = ["Review formatting manually"]
                elif key == 'tone_grammar':
                    analysis_result[key] = "Not provided"
                elif key == 'summary':
                    analysis_result[key] = "Analysis completed but some details were not provided."
                elif key == 'improvements':
                    analysis_result[key] = ["Review the AI response manually for detailed feedback."]
        
        # Ensure numeric values are properly formatted
        if isinstance(analysis_result['score'], str):
            try:
                analysis_result['score'] = int(analysis_result['score'])
            except:
                analysis_result['score'] = 75
        
        if isinstance(analysis_result['skills_match'], str):
            try:
                analysis_result['skills_match'] = int(analysis_result['skills_match'])
            except:
                analysis_result['skills_match'] = 70
        
        # Ensure lists are properly formatted
        if not isinstance(analysis_result['missing_keywords'], list):
            analysis_result['missing_keywords'] = [str(analysis_result['missing_keywords'])]
        
        if not isinstance(analysis_result['found_skills'], list):
            analysis_result['found_skills'] = [str(analysis_result['found_skills'])]
        
        if not isinstance(analysis_result['additional_skills'], list):
            analysis_result['additional_skills'] = [str(analysis_result['additional_skills'])]
        
        if not isinstance(analysis_result['formatting_issues'], list):
            analysis_result['formatting_issues'] = [str(analysis_result['formatting_issues'])]
        
        if not isinstance(analysis_result['improvements'], list):
            analysis_result['improvements'] = [str(analysis_result['improvements'])]
        
        return analysis_result
        
    except Exception as e:
        st.error(f"Error during AI analysis: {str(e)}")
        # Return fallback analysis
        return {
            "score": 0,
            "skills_match": 0,
            "missing_keywords": ["analysis_failed"],
            "found_skills": ["analysis_failed"],
            "required_skills_count": 0,
            "found_skills_count": 0,
            "missing_skills_count": 0,
            "additional_skills": ["analysis_failed"],
            "formatting_issues": ["analysis_failed"],
            "tone_grammar": f"Analysis failed: {str(e)}",
            "summary": f"Analysis failed: {str(e)}. Please check that Ollama is running and the model is installed.",
            "improvements": ["Please check that Ollama is running and the model is installed. Try running 'ollama list' to see available models."]
        }


def generate_cover_letter(resume_text: str, jd_text: str, tone: str = "formal", model_name: str = "llama3.1", use_hf: bool = False, hf_token: Optional[str] = None) -> str:
    """
    Generate a professional cover letter based on resume and job description with specified tone.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        tone: Desired tone for the cover letter ("formal", "confident", "enthusiastic")
        model_name: Name of the Ollama model to use (default: llama3.1)
        
    Returns:
        str: Generated cover letter text
    """
    try:
        # Define tone-specific instructions
        tone_instructions = {
            "formal": "Use a professional, respectful, and traditional tone. Focus on qualifications and experience with measured enthusiasm.",
            "confident": "Use a strong, assertive tone that demonstrates self-assurance and capability. Highlight achievements and leadership qualities.",
            "enthusiastic": "Use an energetic, passionate tone that shows excitement for the opportunity. Emphasize motivation and eagerness to contribute."
        }
        
        tone_instruction = tone_instructions.get(tone, tone_instructions["formal"])
        
        # Create the prompt for cover letter generation
        prompt = f"""
        You are an expert professional writer and career coach. Generate a compelling, professional cover letter based on the provided resume and job description.
        
        Resume:
        {resume_text}
        
        Job Description:
        {jd_text}
        
        Tone Requirement: {tone_instruction}
        
        Please generate a professional cover letter that:
        1. Addresses the hiring manager professionally
        2. Highlights relevant skills and experience from the resume that match the job requirements
        3. Shows enthusiasm for the position and company
        4. Includes specific examples of achievements that relate to the job description
        5. Uses the specified tone: {tone}
        6. Is approximately 250 words (not exceeding 300 words)
        7. Ends with a call to action requesting an interview
        8. Has proper professional structure with clear paragraphs
        
        Format the cover letter with proper paragraphs and professional structure. Do not include any JSON formatting or extra text - just the cover letter content.
        """
        
        # Choose API based on use_hf parameter
        if use_hf and HF_AVAILABLE:
            # Use Hugging Face API
            hf_client = get_hf_client(hf_token)
            if not hf_client:
                raise Exception("Hugging Face client not available. Please check your API token.")
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert professional writer specializing in cover letters and career documents. Generate compelling, personalized cover letters that highlight relevant experience and skills. Use a {tone} tone as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            cover_letter = hf_chat_completion(hf_client, model_name, messages, max_tokens=1000)
            if not cover_letter:
                raise Exception("Failed to get response from Hugging Face API")
        else:
            # Use Ollama API
            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert professional writer specializing in cover letters and career documents. Generate compelling, personalized cover letters that highlight relevant experience and skills. Use a {tone} tone as requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            cover_letter = response['message']['content'].strip()
        
        # Clean up the response if needed
        if cover_letter.startswith('```') and cover_letter.endswith('```'):
            cover_letter = cover_letter[3:-3].strip()
        
        # Ensure the cover letter is not too long
        word_count = len(cover_letter.split())
        if word_count > 300:
            # Truncate to approximately 250 words
            words = cover_letter.split()
            cover_letter = ' '.join(words[:250]) + "..."
        
        return cover_letter
        
    except Exception as e:
        st.error(f"Error generating cover letter: {str(e)}")
        # Return a fallback cover letter
        return f"""Dear Hiring Manager,

I am writing to express my interest in the position at your company. Based on my review of the job description and my professional background, I believe I would be a valuable addition to your team.

Unfortunately, there was an error generating a personalized cover letter. Please ensure that:
1. Ollama is running properly
2. The selected model is available
3. Both resume and job description texts are provided

I apologize for this inconvenience and would be happy to provide additional information about my qualifications.

Best regards,
[Your Name]"""


def preprocess_text_for_visualization(text: str) -> str:
    """
    Preprocess text for visualization by removing common stop words and cleaning.
    
    Args:
        text: Raw text to preprocess
        
    Returns:
        str: Cleaned text suitable for word cloud and analysis
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def get_word_frequencies(text: str, max_words: int = 50) -> Dict[str, int]:
    """
    Get word frequencies from text, excluding common stop words.
    
    Args:
        text: Text to analyze
        max_words: Maximum number of words to return
        
    Returns:
        dict: Word frequency dictionary
    """
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
        'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn',
        'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'
    }
    
    # Preprocess text
    cleaned_text = preprocess_text_for_visualization(text)
    
    # Split into words and filter
    words = [word for word in cleaned_text.split() if word not in stop_words and len(word) > 2]
    
    # Count frequencies
    word_freq = Counter(words)
    
    # Return top words
    return dict(word_freq.most_common(max_words))


def create_word_cloud(text: str, title: str = "Word Cloud") -> Figure:
    """
    Create a word cloud visualization from text.
    
    Args:
        text: Text to create word cloud from
        title: Title for the word cloud
        
    Returns:
        matplotlib.Figure: Word cloud figure
    """
    if not text:
        # Create empty figure
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No text available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return fig
    
    # Get word frequencies
    word_freq = get_word_frequencies(text, max_words=100)
    
    if not word_freq:
        # Create empty figure
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No meaningful words found', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return fig
    
    # Create word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=50,
        relative_scaling=0.5,  # type: ignore
        random_state=42
    ).generate_from_frequencies(word_freq)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    return fig


def analyze_ats_score(resume_text: str, jd_text: str, model_name: str = "llama3.1", use_hf: bool = False, hf_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze resume for ATS optimization and provide detailed improvement recommendations.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        model_name: Name of the Ollama model to use (default: llama3.1)
        
    Returns:
        dict: ATS analysis results with scores and recommendations
    """
    try:
        # Create the ATS analysis prompt
        prompt = f"""
        Analyze this resume for ATS (Applicant Tracking System) optimization and provide detailed recommendations.
        
        Resume:
        {resume_text}
        
        Job Description:
        {jd_text}
        
        Please provide your ATS analysis in the following JSON format:
        {{
            "ats_score": <overall ATS score between 0-100>,
            "keyword_match_score": <keyword matching score between 0-100>,
            "formatting_score": <formatting and structure score between 0-100>,
            "content_score": <content quality score between 0-100>,
            "missing_keywords": ["<keyword 1>", "<keyword 2>", "<keyword 3>", "<keyword 4>", "<keyword 5>"],
            "formatting_issues": ["<issue 1>", "<issue 2>", "<issue 3>"],
            "content_issues": ["<issue 1>", "<issue 2>", "<issue 3>"],
            "ats_optimization_tips": ["<tip 1>", "<tip 2>", "<tip 3>", "<tip 4>", "<tip 5>"],
            "keyword_suggestions": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"],
            "structure_recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"],
            "summary": "<2-line summary of ATS optimization status>"
        }}
        
        ATS Analysis Guidelines:
        1. ATS Score: Overall compatibility with ATS systems (keywords, formatting, structure)
        2. Keyword Match: Percentage of job description keywords found in resume
        3. Formatting Score: How well the resume follows ATS-friendly formatting
        4. Content Score: Quality and relevance of content for the specific job
        5. Missing Keywords: Important job description keywords not found in resume
        6. Formatting Issues: Problems that could affect ATS parsing
        7. Content Issues: Content problems that reduce ATS effectiveness
        8. ATS Optimization Tips: Specific actions to improve ATS performance
        9. Keyword Suggestions: Additional keywords to include
        10. Structure Recommendations: How to improve resume structure for ATS
        11. Summary: Concise overview of ATS optimization status
        
        Focus on practical, actionable advice for improving ATS compatibility.
        Only respond with valid JSON. Do not include any other text or explanations outside the JSON structure.
        """
        
        # Choose API based on use_hf parameter
        if use_hf and HF_AVAILABLE:
            # Use Hugging Face API
            hf_client = get_hf_client(hf_token)
            if not hf_client:
                raise Exception("Hugging Face client not available. Please check your API token.")
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert ATS optimization specialist with deep knowledge of applicant tracking systems, resume parsing, and recruitment technology. Provide comprehensive, actionable ATS optimization advice in the exact JSON format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response_content = hf_chat_completion(hf_client, model_name, messages, max_tokens=2000)
            if not response_content:
                raise Exception("Failed to get response from Hugging Face API")
        else:
            # Use Ollama API
            response = ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ATS optimization specialist with deep knowledge of applicant tracking systems, resume parsing, and recruitment technology. Provide comprehensive, actionable ATS optimization advice in the exact JSON format requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            response_content = response['message']['content'].strip()
        
        # Parse JSON response
        try:
            # Try to extract JSON from the response (in case there's extra text)
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_content[start_idx:end_idx]
                ats_result = json.loads(json_str)
            else:
                ats_result = json.loads(response_content)
                
        except json.JSONDecodeError as e:
            # Fallback: create a structured response from the text
            st.warning("Could not parse AI response as JSON. Using fallback ATS analysis.")
            ats_result = {
                "ats_score": 75,
                "keyword_match_score": 70,
                "formatting_score": 80,
                "content_score": 75,
                "missing_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
                "formatting_issues": ["Review formatting manually"],
                "content_issues": ["Review content manually"],
                "ats_optimization_tips": ["Review the AI response manually for detailed feedback."],
                "keyword_suggestions": ["keyword1", "keyword2", "keyword3"],
                "structure_recommendations": ["Review structure manually"],
                "summary": "Analysis completed but response format was unexpected. Please review the AI response manually for detailed feedback."
            }
        
        # Validate and ensure all required keys exist
        required_keys = ['ats_score', 'keyword_match_score', 'formatting_score', 'content_score', 'missing_keywords', 'formatting_issues', 'content_issues', 'ats_optimization_tips', 'keyword_suggestions', 'structure_recommendations', 'summary']
        for key in required_keys:
            if key not in ats_result:
                if key == 'ats_score':
                    ats_result[key] = 75
                elif key == 'keyword_match_score':
                    ats_result[key] = 70
                elif key == 'formatting_score':
                    ats_result[key] = 80
                elif key == 'content_score':
                    ats_result[key] = 75
                elif key == 'missing_keywords':
                    ats_result[key] = ["keyword1", "keyword2", "keyword3"]
                elif key == 'formatting_issues':
                    ats_result[key] = ["Review formatting manually"]
                elif key == 'content_issues':
                    ats_result[key] = ["Review content manually"]
                elif key == 'ats_optimization_tips':
                    ats_result[key] = ["Review the AI response manually for detailed feedback."]
                elif key == 'keyword_suggestions':
                    ats_result[key] = ["keyword1", "keyword2", "keyword3"]
                elif key == 'structure_recommendations':
                    ats_result[key] = ["Review structure manually"]
                elif key == 'summary':
                    ats_result[key] = "Analysis completed but some details were not provided."
        
        # Ensure numeric values are properly formatted
        numeric_keys = ['ats_score', 'keyword_match_score', 'formatting_score', 'content_score']
        for key in numeric_keys:
            if isinstance(ats_result[key], str):
                try:
                    ats_result[key] = int(ats_result[key])
                except:
                    ats_result[key] = 75
        
        # Ensure lists are properly formatted
        list_keys = ['missing_keywords', 'formatting_issues', 'content_issues', 'ats_optimization_tips', 'keyword_suggestions', 'structure_recommendations']
        for key in list_keys:
            if not isinstance(ats_result[key], list):
                ats_result[key] = [str(ats_result[key])]
        
        return ats_result
        
    except Exception as e:
        st.error(f"Error during ATS analysis: {str(e)}")
        # Return fallback analysis
        return {
            "ats_score": 0,
            "keyword_match_score": 0,
            "formatting_score": 0,
            "content_score": 0,
            "missing_keywords": ["analysis_failed"],
            "formatting_issues": ["analysis_failed"],
            "content_issues": ["analysis_failed"],
            "ats_optimization_tips": ["Please check that Ollama is running and the model is installed."],
            "keyword_suggestions": ["analysis_failed"],
            "structure_recommendations": ["analysis_failed"],
            "summary": f"ATS analysis failed: {str(e)}. Please check that Ollama is running and the model is installed."
        }


def create_skills_bar_chart(resume_text: str, jd_text: str) -> go.Figure:
    """
    Create a bar chart showing top skills and their presence in resume vs job description.
    
    Args:
        resume_text: Resume text
        jd_text: Job description text
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Common skills/keywords to look for
    common_skills = [
        'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'vue', 'node.js',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'ai', 'data analysis',
        'excel', 'powerpoint', 'word', 'project management', 'agile', 'scrum', 'leadership',
        'communication', 'teamwork', 'problem solving', 'analytical', 'research', 'writing',
        'marketing', 'sales', 'customer service', 'finance', 'accounting', 'design', 'creative',
        'management', 'supervision', 'training', 'mentoring', 'strategy', 'planning', 'organization'
    ]
    
    # Preprocess texts
    resume_clean = preprocess_text_for_visualization(resume_text)
    jd_clean = preprocess_text_for_visualization(jd_text)
    
    # Count skill occurrences
    skills_data = []
    for skill in common_skills:
        resume_count = resume_clean.count(skill)
        jd_count = jd_clean.count(skill)
        
        if resume_count > 0 or jd_count > 0:
            skills_data.append({
                'skill': skill.title(),
                'resume_count': resume_count,
                'jd_count': jd_count,
                'total_count': resume_count + jd_count
            })
    
    # Sort by total count and get top 10
    skills_data.sort(key=lambda x: x['total_count'], reverse=True)
    top_skills = skills_data[:10]
    
    if not top_skills:
        # Create empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No skills found in the provided texts",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="Top Skills Analysis",
            xaxis_title="Skills",
            yaxis_title="Count"
        )
        return fig
    
    # Create bar chart
    fig = go.Figure()
    
    # Add resume bars
    fig.add_trace(go.Bar(
        name='Resume',
        x=[skill['skill'] for skill in top_skills],
        y=[skill['resume_count'] for skill in top_skills],
        marker_color='#1f77b4',
        opacity=0.8
    ))
    
    # Add job description bars
    fig.add_trace(go.Bar(
        name='Job Description',
        x=[skill['skill'] for skill in top_skills],
        y=[skill['jd_count'] for skill in top_skills],
        marker_color='#ff7f0e',
        opacity=0.8
    ))
    
    # Update layout
    fig.update_layout(
        title="Top Skills Analysis: Resume vs Job Description",
        xaxis_title="Skills",
        yaxis_title="Occurrence Count",
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig 