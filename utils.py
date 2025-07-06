import fitz  # PyMuPDF
from docx import Document
import streamlit as st
from typing import Optional, Dict, Any
import json
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from collections import Counter
import numpy as np
import re

# Google Gemini imports will be added here
# import google.generativeai as genai


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


def analyze_resume_vs_jd(resume_text: str, jd_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze resume against job description using Google Gemini AI.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        api_key: Google Gemini API key
        
    Returns:
        dict: Detailed analysis results with comprehensive feedback
    """
    try:
        # TODO: Implement Google Gemini integration
        # This is a placeholder that will be replaced with actual Gemini API calls
        
        # For now, return a structured analysis template
        analysis_result = {
            "score": 75,
            "skills_match": 70,
            "missing_keywords": ["python", "machine learning", "data analysis", "project management", "leadership"],
            "found_skills": ["communication", "teamwork", "problem solving", "analytical", "research"],
            "required_skills_count": 8,
            "found_skills_count": 5,
            "missing_skills_count": 3,
            "additional_skills": ["writing", "presentation", "organization"],
            "formatting_issues": ["Consider adding more bullet points", "Improve section organization"],
            "tone_grammar": "Professional tone with good grammar structure.",
            "summary": "Good overall match with room for improvement in technical skills and formatting.",
            "improvements": [
                "Add more technical keywords from the job description",
                "Improve bullet point formatting for better readability",
                "Include specific metrics and achievements",
                "Add relevant certifications or training",
                "Enhance the summary section with key accomplishments"
            ]
        }
        
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
            "summary": f"Analysis failed: {str(e)}. Please check your Google Gemini API key and try again.",
            "improvements": ["Please check your Google Gemini API key and ensure the service is available."]
        }


def generate_cover_letter(resume_text: str, jd_text: str, tone: str = "formal", api_key: Optional[str] = None, custom_prompt: str = "") -> str:
    """
    Generate a professional cover letter based on resume and job description with specified tone.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        tone: Desired tone for the cover letter ("formal", "confident", "enthusiastic")
        api_key: Google Gemini API key
        custom_prompt: Additional custom instructions for generation
        
    Returns:
        str: Generated cover letter text
    """
    try:
        # TODO: Implement Google Gemini integration
        # This is a placeholder that will be replaced with actual Gemini API calls
        
        # Extract key information from job description
        jd_lines = jd_text.split('\n')
        company_name = "the company"
        position_title = "the position"
        
        # Try to extract company and position info
        for line in jd_lines[:10]:  # Check first 10 lines
            line_lower = line.lower()
            if 'company' in line_lower or 'organization' in line_lower:
                company_name = line.strip()
            if 'position' in line_lower or 'role' in line_lower or 'job' in line_lower:
                position_title = line.strip()
        
        # Generate tone-specific content
        if tone == "formal":
            opening = f"I am writing to express my sincere interest in {position_title} at {company_name}."
            confidence = "I am confident that my qualifications and experience align well with your requirements."
            enthusiasm = "I am excited about the opportunity to contribute to your organization."
        elif tone == "confident":
            opening = f"I am excited to apply for {position_title} at {company_name}."
            confidence = "I am confident that my proven track record and skills make me an excellent candidate for this role."
            enthusiasm = "I am eager to bring my expertise and drive results for your team."
        else:  # enthusiastic
            opening = f"I am thrilled to apply for {position_title} at {company_name}!"
            confidence = "I am confident that my passion and experience make me the perfect fit for this exciting opportunity."
            enthusiasm = "I am incredibly excited about the possibility of joining your dynamic team!"
        
        # Add custom prompt instructions if provided
        custom_instruction = ""
        if custom_prompt:
            custom_instruction = f"\n\nAdditional Instructions: {custom_prompt}"
        
        # Create dynamic cover letter
        cover_letter = f"""{opening}

{confidence} Based on my review of the job description and my professional background, I believe I would be a valuable addition to your team.

My experience includes relevant skills and achievements that directly align with the requirements you've outlined. {enthusiasm}

I am particularly drawn to this opportunity because of the company's reputation for innovation and excellence. I am eager to bring my expertise to your team and help drive continued success.{custom_instruction}

Thank you for considering my application. I look forward to discussing how my background, skills, and enthusiasm can contribute to your team.

Best regards,
[Your Name]"""
        
        return cover_letter
        
    except Exception as e:
        st.error(f"Error generating cover letter: {str(e)}")
        # Return a fallback cover letter
        return f"""Dear Hiring Manager,

I am writing to express my interest in the position at your company. Based on my review of the job description and my professional background, I believe I would be a valuable addition to your team.

Unfortunately, there was an error generating a personalized cover letter. Please ensure that:
1. Google Gemini API is properly configured
2. Your API key is valid and has the necessary permissions
3. Both resume and job description texts are provided

I apologize for this inconvenience and would be happy to provide additional information about my qualifications.

Best regards,
[Your Name]"""


def analyze_ats_score(resume_text: str, jd_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze resume for ATS optimization and provide detailed improvement recommendations.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        api_key: Google Gemini API key
        
    Returns:
        dict: ATS analysis results with scores and recommendations
    """
    try:
        # TODO: Implement Google Gemini integration
        # This is a placeholder that will be replaced with actual Gemini API calls
        
        ats_result = {
            "ats_score": 75,
            "keyword_match_score": 70,
            "formatting_score": 80,
            "content_score": 75,
            "missing_keywords": ["python", "machine learning", "data analysis", "project management", "leadership"],
            "formatting_issues": ["Consider using standard fonts", "Improve bullet point consistency"],
            "content_issues": ["Add more specific achievements", "Include relevant certifications"],
            "ats_optimization_tips": [
                "Use standard fonts like Arial or Times New Roman",
                "Include relevant keywords from the job description",
                "Use clear section headings",
                "Avoid graphics and tables that may not parse well",
                "Keep formatting simple and clean"
            ],
            "keyword_suggestions": ["python", "data analysis", "project management"],
            "structure_recommendations": [
                "Use clear section headers",
                "Include a professional summary",
                "List experience in reverse chronological order"
            ],
            "summary": "Good ATS compatibility with room for improvement in keyword optimization and formatting."
        }
        
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
            "ats_optimization_tips": ["Please check your Google Gemini API key and ensure the service is available."],
            "keyword_suggestions": ["analysis_failed"],
            "structure_recommendations": ["analysis_failed"],
            "summary": f"ATS analysis failed: {str(e)}. Please check your Google Gemini API key and try again."
        }


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