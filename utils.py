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
import pandas as pd

# Google Gemini imports will be added here
# import google.generativeai as genai

# Try to import optional dependencies
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


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
    Analyze resume for ATS optimization using advanced NLP techniques.
    
    Args:
        resume_text: Extracted text from resume
        jd_text: Extracted text from job description
        api_key: Google Gemini API key
        
    Returns:
        dict: ATS analysis results with scores and recommendations
    """
    try:
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        # Preprocess texts
        resume_clean = preprocess_text_for_ats(resume_text)
        jd_clean = preprocess_text_for_ats(jd_text)
        
        # Calculate TF-IDF similarity
        tfidf_similarity = calculate_tfidf_similarity(resume_clean, jd_clean)
        
        # Extract and analyze keywords
        keyword_analysis = analyze_keywords(resume_clean, jd_clean)
        
        # Analyze formatting and structure
        formatting_analysis = analyze_formatting(resume_text)
        
        # Calculate content quality score
        content_analysis = analyze_content_quality(resume_text, jd_text)
        
        # Calculate overall ATS score
        ats_score = calculate_overall_ats_score(
            tfidf_similarity, 
            keyword_analysis, 
            formatting_analysis, 
            content_analysis
        )
        
        # Generate comprehensive results
        ats_result = {
            "ats_score": ats_score,
            "keyword_match_score": keyword_analysis["match_percentage"],
            "formatting_score": formatting_analysis["formatting_score"],
            "content_score": content_analysis["content_score"],
            "tfidf_similarity": tfidf_similarity,
            "missing_keywords": keyword_analysis["missing_keywords"],
            "found_keywords": keyword_analysis["found_keywords"],
            "keyword_density": keyword_analysis["keyword_density"],
            "formatting_issues": formatting_analysis["issues"],
            "content_issues": content_analysis["issues"],
            "ats_optimization_tips": generate_ats_tips(keyword_analysis, formatting_analysis, content_analysis),
            "keyword_suggestions": keyword_analysis["suggestions"],
            "structure_recommendations": formatting_analysis["recommendations"],
            "summary": generate_ats_summary(ats_score, keyword_analysis, formatting_analysis),
            "detailed_stats": {
                "total_keywords_found": len(keyword_analysis["found_keywords"]),
                "total_keywords_missing": len(keyword_analysis["missing_keywords"]),
                "keyword_coverage": keyword_analysis["match_percentage"],
                "text_length": len(resume_text),
                "word_count": len(resume_text.split()),
                "sentence_count": len(re.split(r'[.!?]+', resume_text)),
                "paragraph_count": len([p for p in resume_text.split('\n\n') if p.strip()])
            }
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


def preprocess_text_for_ats(text: str) -> str:
    """
    Preprocess text specifically for ATS analysis.
    
    Args:
        text: Raw text to preprocess
        
    Returns:
        str: Cleaned text suitable for ATS analysis
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep important ones
    text = re.sub(r'[^\w\s\-\.]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

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


def calculate_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculate TF-IDF similarity between resume and job description.
    
    Args:
        resume_text: Cleaned resume text
        jd_text: Cleaned job description text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    if not SKLEARN_AVAILABLE:
        return 0.5  # Fallback score
    
    try:
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
        # Fit and transform the texts
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
        
    except Exception:
        return 0.5  # Fallback score


def analyze_keywords(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Analyze keywords in resume vs job description.
    
    Args:
        resume_text: Cleaned resume text
        jd_text: Cleaned job description text
        
    Returns:
        dict: Keyword analysis results
    """
    # Extract keywords from job description
    jd_words = set(jd_text.lower().split())
    resume_words = set(resume_text.lower().split())
    
    # Common professional keywords
    professional_keywords = {
        'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'vue',
        'node.js', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'machine learning',
        'ai', 'data analysis', 'excel', 'powerpoint', 'word', 'project management',
        'agile', 'scrum', 'leadership', 'communication', 'teamwork', 'problem solving',
        'analytical', 'research', 'writing', 'marketing', 'sales', 'customer service',
        'finance', 'accounting', 'design', 'creative', 'management', 'supervision',
        'training', 'mentoring', 'strategy', 'planning', 'organization'
    }
    
    # Find relevant keywords in job description
    jd_keywords = jd_words.intersection(professional_keywords)
    
    # Find matching keywords in resume
    found_keywords = resume_words.intersection(jd_keywords)
    missing_keywords = jd_keywords - found_keywords
    
    # Calculate match percentage
    match_percentage = (len(found_keywords) / len(jd_keywords) * 100) if jd_keywords else 0
    
    # Calculate keyword density
    total_words = len(resume_text.split())
    keyword_density = (len(found_keywords) / total_words * 100) if total_words > 0 else 0
    
    # Generate suggestions
    suggestions = list(missing_keywords)[:10]  # Top 10 missing keywords
    
    return {
        "found_keywords": list(found_keywords),
        "missing_keywords": list(missing_keywords),
        "match_percentage": match_percentage,
        "keyword_density": keyword_density,
        "suggestions": suggestions
    }


def analyze_formatting(resume_text: str) -> Dict[str, Any]:
    """
    Analyze resume formatting and structure.
    
    Args:
        resume_text: Raw resume text
        
    Returns:
        dict: Formatting analysis results
    """
    issues = []
    recommendations = []
    formatting_score = 100
    
    # Check for bullet points
    bullet_patterns = [r'•', r'\-', r'\*', r'→', r'▶']
    has_bullets = any(re.search(pattern, resume_text) for pattern in bullet_patterns)
    
    if not has_bullets:
        issues.append("No bullet points found - consider using bullet points for better readability")
        recommendations.append("Add bullet points (•, -, *) to highlight achievements and responsibilities")
        formatting_score -= 15
    
    # Check for section headers
    section_headers = ['experience', 'education', 'skills', 'summary', 'objective', 'work history']
    has_sections = any(header in resume_text.lower() for header in section_headers)
    
    if not has_sections:
        issues.append("No clear section headers found")
        recommendations.append("Add clear section headers like 'Experience', 'Education', 'Skills'")
        formatting_score -= 20
    
    # Check text length
    word_count = len(resume_text.split())
    if word_count < 100:
        issues.append("Resume appears too short")
        recommendations.append("Add more content to make your resume comprehensive")
        formatting_score -= 10
    elif word_count > 800:
        issues.append("Resume appears too long")
        recommendations.append("Consider condensing content to 1-2 pages")
        formatting_score -= 5
    
    # Check for contact information
    contact_patterns = [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b']
    has_contact = any(re.search(pattern, resume_text) for pattern in contact_patterns)
    
    if not has_contact:
        issues.append("No contact information found")
        recommendations.append("Add email and phone number")
        formatting_score -= 10
    
    return {
        "formatting_score": max(0, formatting_score),
        "issues": issues,
        "recommendations": recommendations
    }


def analyze_content_quality(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Analyze content quality of resume.
    
    Args:
        resume_text: Resume text
        jd_text: Job description text
        
    Returns:
        dict: Content quality analysis results
    """
    issues = []
    content_score = 100
    
    # Check for action verbs
    action_verbs = [
        'developed', 'implemented', 'managed', 'created', 'designed', 'analyzed',
        'improved', 'increased', 'decreased', 'coordinated', 'led', 'supervised',
        'trained', 'mentored', 'researched', 'evaluated', 'optimized', 'streamlined'
    ]
    
    resume_lower = resume_text.lower()
    action_verb_count = sum(1 for verb in action_verbs if verb in resume_lower)
    
    if action_verb_count < 3:
        issues.append("Limited use of action verbs")
        content_score -= 15
    
    # Check for metrics/numbers
    metric_pattern = r'\d+%|\d+\s*(percent|dollars?|users?|customers?|projects?|years?)'
    has_metrics = bool(re.search(metric_pattern, resume_text, re.IGNORECASE))
    
    if not has_metrics:
        issues.append("No quantifiable achievements found")
        content_score -= 20
    
    # Check for specific skills mentioned in JD
    jd_words = set(jd_text.lower().split())
    resume_words = set(resume_text.lower().split())
    skill_overlap = len(jd_words.intersection(resume_words))
    
    if skill_overlap < 5:
        issues.append("Limited skill overlap with job description")
        content_score -= 25
    
    return {
        "content_score": max(0, content_score),
        "issues": issues
    }


def calculate_overall_ats_score(tfidf_similarity: float, keyword_analysis: Dict, 
                               formatting_analysis: Dict, content_analysis: Dict) -> float:
    """
    Calculate overall ATS score based on all analyses.
    
    Args:
        tfidf_similarity: TF-IDF similarity score
        keyword_analysis: Keyword analysis results
        formatting_analysis: Formatting analysis results
        content_analysis: Content quality analysis results
        
    Returns:
        float: Overall ATS score (0-100)
    """
    # Weighted scoring
    tfidf_weight = 0.3
    keyword_weight = 0.3
    formatting_weight = 0.2
    content_weight = 0.2
    
    # Calculate weighted score
    tfidf_score = tfidf_similarity * 100
    keyword_score = keyword_analysis.get("match_percentage", 0)
    formatting_score = formatting_analysis.get("formatting_score", 0)
    content_score = content_analysis.get("content_score", 0)
    
    overall_score = (
        tfidf_score * tfidf_weight +
        keyword_score * keyword_weight +
        formatting_score * formatting_weight +
        content_score * content_weight
    )
    
    return round(overall_score, 1)


def generate_ats_tips(keyword_analysis: Dict, formatting_analysis: Dict, 
                     content_analysis: Dict) -> list:
    """
    Generate ATS optimization tips based on analysis results.
    
    Args:
        keyword_analysis: Keyword analysis results
        formatting_analysis: Formatting analysis results
        content_analysis: Content quality analysis results
        
    Returns:
        list: List of optimization tips
    """
    tips = []
    
    # Keyword tips
    if keyword_analysis.get("match_percentage", 0) < 50:
        tips.append("Add more keywords from the job description to improve ATS matching")
    
    if keyword_analysis.get("missing_keywords"):
        tips.append(f"Consider adding these keywords: {', '.join(keyword_analysis['missing_keywords'][:5])}")
    
    # Formatting tips
    if formatting_analysis.get("issues"):
        tips.extend(formatting_analysis["issues"][:3])
    
    # Content tips
    if content_analysis.get("issues"):
        tips.extend(content_analysis["issues"][:3])
    
    # General tips
    tips.extend([
        "Use standard section headers (Experience, Education, Skills)",
        "Include quantifiable achievements with numbers and percentages",
        "Use action verbs to start bullet points",
        "Keep formatting simple and avoid graphics or tables",
        "Ensure contact information is clearly visible"
    ])
    
    return tips[:10]  # Return top 10 tips


def generate_ats_summary(ats_score: float, keyword_analysis: Dict, 
                        formatting_analysis: Dict) -> str:
    """
    Generate a summary of ATS analysis results.
    
    Args:
        ats_score: Overall ATS score
        keyword_analysis: Keyword analysis results
        formatting_analysis: Formatting analysis results
        
    Returns:
        str: Summary text
    """
    if ats_score >= 80:
        summary = "Excellent ATS optimization! Your resume is well-structured and keyword-optimized."
    elif ats_score >= 60:
        summary = "Good ATS optimization with room for improvement in keyword matching and formatting."
    elif ats_score >= 40:
        summary = "Fair ATS optimization. Consider adding more relevant keywords and improving structure."
    else:
        summary = "Poor ATS optimization. Significant improvements needed in keywords, formatting, and content."
    
    keyword_match = keyword_analysis.get("match_percentage", 0)
    if keyword_match < 50:
        summary += f" Only {keyword_match:.1f}% of job description keywords were found in your resume."
    
    return summary 