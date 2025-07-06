import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import gray
from io import BytesIO
from utils import extract_text_from_file, get_file_info, validate_file_type, analyze_resume_vs_jd, analyze_ats_score, generate_cover_letter

# Set page config
st.set_page_config(
    page_title="myAIHr - AI-Powered Resume Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for session state management
def create_gauge_chart(value, title, color="blue"):
    """Create a gauge chart for displaying scores."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "lightgray"},
                {'range': [30, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def generate_pdf(cover_letter_text, tone):
    """Generate a PDF file from cover letter text."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Add title
    story.append(Paragraph("Cover Letter", title_style))
    story.append(Spacer(1, 20))
    
    # Add metadata
    metadata_style = ParagraphStyle(
        'Metadata',
        parent=styles['Normal'],
        fontSize=10,
        textColor=gray,
        alignment=1
    )
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", metadata_style))
    story.append(Paragraph(f"Tone: {tone.title()}", metadata_style))
    story.append(Spacer(1, 30))
    
    # Add cover letter content
    paragraphs = cover_letter_text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), normal_style))
            story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def save_analysis_to_history(resume_text, job_text, analysis_results, model_used):
    """Save analysis results to session state history."""
    import datetime
    
    analysis_entry = {
        'id': len(st.session_state.analysis_history) + 1,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'resume_text': resume_text,
        'job_text': job_text,
        'analysis_results': analysis_results,
        'model_used': model_used,
        'resume_words': len(resume_text.split()) if resume_text else 0,
        'job_words': len(job_text.split()) if job_text else 0,
        'score': analysis_results.get('score', 0) if analysis_results else 0
    }
    
    st.session_state.analysis_history.append(analysis_entry)
    st.session_state.current_analysis_id = analysis_entry['id']
    
    # Keep only last 10 analyses to prevent memory issues
    if len(st.session_state.analysis_history) > 10:
        st.session_state.analysis_history = st.session_state.analysis_history[-10:]

def load_analysis_from_history(analysis_id):
    """Load analysis from history by ID."""
    for entry in st.session_state.analysis_history:
        if entry['id'] == analysis_id:
            st.session_state.resume_text = entry['resume_text']
            st.session_state.job_text = entry['job_text']
            st.session_state.analysis_results = entry['analysis_results']
            st.session_state.current_analysis_id = entry['id']
            return entry
    return None

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_text' not in st.session_state:
    st.session_state.job_text = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = None

# Initialize analysis history
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis_id' not in st.session_state:
    st.session_state.current_analysis_id = None

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 1.8rem; color: #1f77b4; margin-bottom: 0.5rem;">🤖 myAIHr</h1>
        <p style="color: #6c757d; font-size: 0.9rem;">AI-Powered Resume Analysis with Google Gemini</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🚀 How to Use")
    st.markdown("""
    1. **Upload** your resume (PDF/DOCX/TXT)
    2. **Enter** job description text
    3. **Analyze** with AI for insights
    4. **Generate** personalized cover letter
    5. **Optimize** for ATS systems
    """)
    
    st.divider()
    
    # Google Gemini Settings
    st.markdown("### 🤖 AI Settings")
    
    # Google Gemini API Key
    gemini_api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get your API key from https://makersuite.google.com/app/apikey",
        placeholder="AIza..."
    )
    
    st.divider()
    
    # Analysis History
    if st.session_state.analysis_history:
        st.markdown("### 📚 Analysis History")
        st.markdown(f"**Total Analyses:** {len(st.session_state.analysis_history)}")
        
        # Create options for selectbox
        history_options = []
        for entry in st.session_state.analysis_history:
            timestamp = entry['timestamp']
            score = entry['score']
            resume_words = entry['resume_words']
            job_words = entry['job_words']
            option_text = f"{timestamp} | Score: {score}% | R:{resume_words}w/J:{job_words}w"
            history_options.append((entry['id'], option_text))
        
        # Selectbox for history
        if history_options:
            selected_history = st.selectbox(
                "Choose Previous Analysis",
                options=[opt[0] for opt in history_options],
                format_func=lambda x: next(opt[1] for opt in history_options if opt[0] == x),
                help="Select a previous analysis to view or re-run"
            )
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📖 Load", use_container_width=True):
                    loaded_entry = load_analysis_from_history(selected_history)
                    if loaded_entry:
                        st.success(f"✅ Loaded analysis from {loaded_entry['timestamp']}")
                        st.rerun()
            
            with col2:
                if st.button("🔄 Re-run", use_container_width=True):
                    loaded_entry = load_analysis_from_history(selected_history)
                    if loaded_entry:
                        st.session_state.analysis_results = None  # Clear current results
                        st.success(f"✅ Ready to re-run analysis from {loaded_entry['timestamp']}")
                        st.rerun()
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True, type="secondary"):
            st.session_state.analysis_history = []
            st.session_state.current_analysis_id = None
            st.success("✅ Analysis history cleared!")
            st.rerun()
            
    else:
        st.markdown("### 📚 Analysis History")
        st.info("No previous analyses yet. Complete your first analysis to see history here.")
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🆕 Start Fresh", use_container_width=True):
        st.session_state.resume_text = ""
        st.session_state.job_text = ""
        st.session_state.analysis_results = None
        st.session_state.cover_letter = None
        st.session_state.current_analysis_id = None
        st.success("✅ Started fresh! Ready for new analysis.")
        st.rerun()
    
    st.divider()
    
    # App Info
    st.markdown("### ℹ️ About")
    st.markdown("""
    **myAIHr** uses Google Gemini AI to analyze resumes against job descriptions and generate personalized cover letters.
    
    Built with Streamlit and Google Gemini.
    """)

# Main content
st.markdown('<h1 class="main-header">🤖 myAIHr</h1>', unsafe_allow_html=True)

# Current analysis indicator
if st.session_state.current_analysis_id:
    current_entry = next((entry for entry in st.session_state.analysis_history if entry['id'] == st.session_state.current_analysis_id), None)
    if current_entry:
        st.info(f"📖 **Currently viewing:** Analysis from {current_entry['timestamp']} (Score: {current_entry['score']}%)")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Analyze", "🤖 AI Feedback", "🎯 ATS Score", "📝 Cover Letter"])

# Tab 1: Upload & Analyze
with tab1:
    st.markdown('<h2 class="section-header">📤 Upload Your Documents</h2>', unsafe_allow_html=True)
    
    # Two columns for upload
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Resume Upload")
        resume_file = st.file_uploader(
            "Upload your resume",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if resume_file:
            file_info = get_file_info(resume_file)
            st.success(f"✅ **{file_info['name']}** uploaded successfully!")
            st.info(f"📊 **File size:** {file_info['size']:,} bytes")
            
            # Auto-extract text on upload
            with st.spinner("🔍 Extracting text from resume..."):
                extracted_text = extract_text_from_file(resume_file)
                if extracted_text:
                    st.session_state.resume_text = extracted_text
                    st.success("✅ Text extracted automatically!")
                    st.info(f"📝 **Word count:** {len(extracted_text.split())} words")
                    st.info(f"📏 **Character count:** {len(extracted_text)} characters")
                else:
                    st.error("❌ Failed to extract text from resume")
            
            # Show extracted text in expander
            if st.session_state.resume_text:
                with st.expander("📄 View Extracted Resume Text", expanded=False):
                    st.text_area(
                        "Resume Text",
                        value=st.session_state.resume_text,
                        height=200,
                        disabled=True
                    )
        else:
            st.info("📄 No resume uploaded yet")
    
    with col2:
        st.markdown("### 💼 Job Description")
        
        # Text input for job description
        jd_text_input = st.text_area(
            "Enter job description text",
            height=200,
            placeholder="Paste the job description here...",
            help="Enter the complete job description text",
            value=st.session_state.job_text if st.session_state.job_text else ""
        )
        
        # Auto-process text input
        if jd_text_input and jd_text_input != st.session_state.job_text:
            st.session_state.job_text = jd_text_input
            st.success("✅ Job description text updated!")
            st.info(f"📝 **Word count:** {len(jd_text_input.split())} words")
        
        # Show current job description text
        if st.session_state.job_text:
            with st.expander("💼 View Job Description Text", expanded=False):
                st.text_area(
                    "Job Description Text",
                    value=st.session_state.job_text,
                    height=200,
                    disabled=True
                )
        else:
            st.info("💼 No job description provided yet")

    # Analysis Button
    st.divider()
    st.markdown('<h2 class="section-header">🤖 AI Analysis</h2>', unsafe_allow_html=True)
    
    # Check if API key is provided
    if not gemini_api_key:
        st.error("❌ Google Gemini API key is required for AI analysis.")
        st.info("💡 Please enter your API key in the sidebar to continue.")
        analyze_button = False
    else:
        analyze_button = st.button("🚀 Analyze Resume vs Job Description", use_container_width=True, type="primary")
    
    # Display current texts
    if st.session_state.resume_text or st.session_state.job_text:
        st.markdown("### 📋 Current Documents")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.resume_text:
                st.markdown("**📄 Resume Text:**")
                st.info(f"✅ {len(st.session_state.resume_text.split())} words, {len(st.session_state.resume_text)} characters")
            else:
                st.info("📝 No resume text available")
        
        with col2:
            if st.session_state.job_text:
                st.markdown("**💼 Job Description Text:**")
                st.info(f"✅ {len(st.session_state.job_text.split())} words, {len(st.session_state.job_text)} characters")
            else:
                st.info("📝 No job description text available")

    # AI Analysis Results
    if analyze_button:
        st.divider()
        st.markdown('<h2 class="section-header">🤖 AI Analysis Results</h2>', unsafe_allow_html=True)
        
        if st.session_state.resume_text and st.session_state.job_text:
            try:
                with st.spinner("🤖 Analyzing resume against job description..."):
                    analysis_results = analyze_resume_vs_jd(
                        st.session_state.resume_text, 
                        st.session_state.job_text, 
                        gemini_api_key
                    )
                    st.session_state.analysis_results = analysis_results
                    
                    # Save to history
                    save_analysis_to_history(
                        st.session_state.resume_text, 
                        st.session_state.job_text, 
                        analysis_results, 
                        "Google Gemini"
                    )
                
                st.success("✅ Analysis completed successfully!")
                st.info("💾 Analysis saved to history. You can view it in the sidebar.")
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Analysis failed: {error_msg}")
                st.info("💡 **Troubleshooting:**")
                st.info("• Check your Google Gemini API key")
                st.info("• Verify the API key has the necessary permissions")
                st.info("• Ensure both resume and job description texts are provided")
        else:
            st.error("❌ Please ensure both resume and job description texts are available for analysis.")

# Tab 2: AI Feedback
with tab2:
    if st.session_state.analysis_results:
        st.markdown('<h2 class="section-header">🤖 AI Analysis Results</h2>', unsafe_allow_html=True)
        
        # Display metrics with progress bars
        col1, col2 = st.columns(2)
        
        with col1:
            score = st.session_state.analysis_results.get('score', 0)
            st.metric(
                label="🎯 Overall Match Score",
                value=f"{score}%",
                delta=f"{score - 50}%" if score > 50 else f"{score - 50}%"
            )
            st.progress(score / 100, text=f"Match Progress: {score}%")
            
            # Experience Level based on score
            if score >= 80:
                exp_level = "Excellent"
                exp_color = "green"
            elif score >= 60:
                exp_level = "Good"
                exp_color = "blue"
            elif score >= 40:
                exp_level = "Fair"
                exp_color = "orange"
            else:
                exp_level = "Poor"
                exp_color = "red"
            
            st.markdown(f"**⭐ Experience Level:** :{exp_color}[{exp_level}]")
        
        with col2:
            skills_match = st.session_state.analysis_results.get('skills_match', 0)
            st.metric(
                label="💪 Skills Match",
                value=f"{skills_match}%",
                delta=f"{skills_match - 50}%" if skills_match > 50 else f"{skills_match - 50}%"
            )
            st.progress(skills_match / 100, text=f"Skills Progress: {skills_match}%")
            
            # Overall Fit based on score
            if score >= 85:
                overall_fit = "Strong"
                fit_color = "green"
            elif score >= 70:
                overall_fit = "Good"
                fit_color = "blue"
            elif score >= 50:
                overall_fit = "Moderate"
                fit_color = "orange"
            else:
                overall_fit = "Weak"
                fit_color = "red"
            
            st.markdown(f"**🎯 Overall Fit:** :{fit_color}[{overall_fit}]")
        
        st.divider()
        
        # Summary Section
        st.markdown("### 📝 AI Summary")
        summary = st.session_state.analysis_results.get('summary', 'No summary available.')
        if summary and not summary.startswith("Analysis failed"):
            st.info(f"**{summary}**")
        else:
            st.warning("**Summary not available or analysis failed.**")
        
        st.divider()
        
        # Missing Keywords Section
        st.markdown("### 🔑 Missing Keywords")
        missing_keywords = st.session_state.analysis_results.get('missing_keywords', [])
        if missing_keywords and missing_keywords != ["analysis_failed"]:
            st.markdown("**Important keywords from the job description that are missing from your resume:**")
            
            # Display keywords as error chips
            keyword_cols = st.columns(3)
            for i, keyword in enumerate(missing_keywords):
                col_idx = i % 3
                with keyword_cols[col_idx]:
                    st.error(f"❌ {keyword}")
        else:
            st.success("✅ No missing keywords identified!")
        
        st.divider()
        
        # Detailed Analysis Sections
        col1, col2 = st.columns(2)
        
        with col1:
            # 💡 Improvement Recommendations
            st.markdown("### 💡 Improvement Recommendations")
            improvements = st.session_state.analysis_results.get('improvements', [])
            if improvements and improvements != ["Please check your Google Gemini API key and ensure the service is available."]:
                for i, improvement in enumerate(improvements, 1):
                    st.markdown(f"**{i}.** {improvement}")
            else:
                st.info("No specific recommendations available at this time.")
            
            # 📝 Tone & Grammar Evaluation
            st.markdown("### 📝 Tone & Grammar Evaluation")
            tone_grammar = st.session_state.analysis_results.get('tone_grammar', 'No evaluation available.')
            if tone_grammar and not tone_grammar.startswith("Analysis failed"):
                st.info(f"**{tone_grammar}**")
            else:
                st.warning("Tone and grammar evaluation not available.")
        
        with col2:
            # ⚠️ Formatting Issues
            st.markdown("### ⚠️ Formatting Issues")
            formatting_issues = st.session_state.analysis_results.get('formatting_issues', [])
            if formatting_issues and formatting_issues != ["analysis_failed"]:
                for i, issue in enumerate(formatting_issues, 1):
                    st.markdown(f"**{i}.** {issue}")
            else:
                st.success("✅ No formatting issues identified!")
            
            # 📌 Skills Analysis Details
            st.markdown("### 📌 Skills Analysis Details")
            skills_match = st.session_state.analysis_results.get('skills_match', 0)
            
            # Get dynamic skills data from AI analysis
            required_skills_count = st.session_state.analysis_results.get('required_skills_count', 0)
            found_skills_count = st.session_state.analysis_results.get('found_skills_count', 0)
            missing_skills_count = st.session_state.analysis_results.get('missing_skills_count', 0)
            found_skills = st.session_state.analysis_results.get('found_skills', [])
            additional_skills = st.session_state.analysis_results.get('additional_skills', [])
            missing_keywords = st.session_state.analysis_results.get('missing_keywords', [])
            
            # Filter out error indicators
            found_skills = [skill for skill in found_skills if skill != "analysis_failed"] if found_skills else []
            additional_skills = [skill for skill in additional_skills if skill != "analysis_failed"] if additional_skills else []
            missing_skills = [kw for kw in missing_keywords if kw != "analysis_failed"] if missing_keywords else []
            
            st.markdown(f"""
            **Skills Match Score:** {skills_match}%
            
            **Analysis Breakdown:**
            - **Required Skills Found:** {found_skills_count} out of {required_skills_count} required skills
            - **Missing Skills:** {missing_skills_count} skills need to be added
            - **Additional Skills:** {len(additional_skills)} bonus skills detected
            """)
            
            # Display found skills
            if found_skills:
                st.markdown("**✅ Skills Found in Your Resume:**")
                skill_cols = st.columns(3)
                for i, skill in enumerate(found_skills[:6]):  # Show top 6 found skills
                    col_idx = i % 3
                    with skill_cols[col_idx]:
                        st.success(f"✅ {skill}")
                if len(found_skills) > 6:
                    st.markdown(f"*... and {len(found_skills) - 6} more skills found*")
            
            # Display missing skills
            if missing_skills:
                st.markdown("**❌ Missing Skills to Add:**")
                missing_cols = st.columns(3)
                for i, skill in enumerate(missing_skills[:6]):  # Show top 6 missing skills
                    col_idx = i % 3
                    with missing_cols[col_idx]:
                        st.error(f"❌ {skill}")
                if len(missing_skills) > 6:
                    st.markdown(f"*... and {len(missing_skills) - 6} more skills missing*")
            
            # Display additional skills
            if additional_skills:
                st.markdown("**🎯 Additional Skills (Bonus):**")
                bonus_cols = st.columns(3)
                for i, skill in enumerate(additional_skills[:6]):  # Show top 6 additional skills
                    col_idx = i % 3
                    with bonus_cols[col_idx]:
                        st.info(f"🎯 {skill}")
                if len(additional_skills) > 6:
                    st.markdown(f"*... and {len(additional_skills) - 6} more bonus skills*")
        
        # Download AI Feedback Report
        st.divider()
        st.markdown("### 📥 Download AI Feedback Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create text report
            report_text = f"""myAIHr - AI Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL ASSESSMENT
==================
Overall Match Score: {st.session_state.analysis_results.get('score', 0)}%
Skills Match: {st.session_state.analysis_results.get('skills_match', 0)}%

SUMMARY
=======
{st.session_state.analysis_results.get('summary', 'No summary available.')}

MISSING KEYWORDS
===============
{chr(10).join([f"• {keyword}" for keyword in st.session_state.analysis_results.get('missing_keywords', [])])}

IMPROVEMENT RECOMMENDATIONS
==========================
{chr(10).join([f"{i+1}. {improvement}" for i, improvement in enumerate(st.session_state.analysis_results.get('improvements', []))])}

TONE & GRAMMAR EVALUATION
=========================
{st.session_state.analysis_results.get('tone_grammar', 'No evaluation available.')}

FORMATTING ISSUES
=================
{chr(10).join([f"• {issue}" for issue in st.session_state.analysis_results.get('formatting_issues', [])])}
"""
            
            st.download_button(
                label="📄 Download as TXT",
                data=report_text,
                file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Create markdown report
            report_md = f"""# myAIHr - AI Analysis Report
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overall Assessment
- **Overall Match Score:** {st.session_state.analysis_results.get('score', 0)}%
- **Skills Match:** {st.session_state.analysis_results.get('skills_match', 0)}%

## Summary
{st.session_state.analysis_results.get('summary', 'No summary available.')}

## Missing Keywords
{chr(10).join([f"- {keyword}" for keyword in st.session_state.analysis_results.get('missing_keywords', [])])}

## Improvement Recommendations
{chr(10).join([f"{i+1}. {improvement}" for i, improvement in enumerate(st.session_state.analysis_results.get('improvements', []))])}

## Tone & Grammar Evaluation
{st.session_state.analysis_results.get('tone_grammar', 'No evaluation available.')}

## Formatting Issues
{chr(10).join([f"- {issue}" for issue in st.session_state.analysis_results.get('formatting_issues', [])])}
"""
            
            st.download_button(
                label="📝 Download as Markdown",
                data=report_md,
                file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    else:
        st.markdown('<h2 class="section-header">🤖 AI Analysis Results</h2>', unsafe_allow_html=True)
        st.info("📊 No analysis results available. Please run an analysis in the 'Upload & Analyze' tab first.")

# Tab 3: ATS Score
with tab3:
    if st.session_state.analysis_results:
        st.markdown('<h2 class="section-header">🎯 ATS Optimization Analysis</h2>', unsafe_allow_html=True)
        
        # ATS Score Analysis
        ats_results = analyze_ats_score(
            st.session_state.resume_text, 
            st.session_state.job_text,
            gemini_api_key
        )
        
        # Display ATS metrics with premium gauge charts
        st.markdown("### 🎯 ATS Score Dashboard")
        
        # Main ATS Score Gauge
        ats_score = ats_results.get('ats_score', 0)
        ats_color = "green" if ats_score >= 80 else "orange" if ats_score >= 60 else "red"
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ats_gauge = create_gauge_chart(ats_score, "Overall ATS Score", ats_color)
            st.plotly_chart(ats_gauge, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Score Breakdown")
            
            # Individual scores
            keyword_match = ats_results.get('keyword_match_score', 0)
            formatting_score = ats_results.get('formatting_score', 0)
            content_score = ats_results.get('content_score', 0)
            
            st.metric("🔑 Keyword Match", f"{keyword_match}%")
            st.metric("📝 Formatting", f"{formatting_score}%")
            st.metric("📄 Content", f"{content_score}%")
            
            # Overall assessment
            if ats_score >= 80:
                st.success("🎉 **Excellent ATS Compatibility**")
                st.info("Your resume should pass most ATS systems!")
            elif ats_score >= 60:
                st.warning("⚠️ **Good ATS Compatibility**")
                st.info("Some improvements recommended for better results.")
            else:
                st.error("❌ **Poor ATS Compatibility**")
                st.info("Significant improvements needed to pass ATS screening.")
        
        st.divider()
        
        # ATS Summary
        st.markdown("### 📋 ATS Summary")
        ats_summary = ats_results.get('summary', 'No ATS summary available.')
        if ats_summary and not ats_summary.startswith("ATS analysis failed"):
            st.info(f"**{ats_summary}**")
        else:
            st.warning("ATS summary not available.")
        
        st.divider()
        
        # Detailed ATS Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Missing Keywords
            st.markdown("### ❌ Missing Keywords")
            missing_keywords = ats_results.get('missing_keywords', [])
            if missing_keywords and missing_keywords != ["analysis_failed"]:
                for keyword in missing_keywords:
                    st.error(f"❌ {keyword}")
            else:
                st.success("✅ No missing keywords identified!")
            
            # Formatting Issues
            st.markdown("### ⚠️ Formatting Issues")
            formatting_issues = ats_results.get('formatting_issues', [])
            if formatting_issues and formatting_issues != ["analysis_failed"]:
                for i, issue in enumerate(formatting_issues, 1):
                    st.markdown(f"**{i}.** {issue}")
            else:
                st.success("✅ No formatting issues identified!")
            
            # Content Issues
            st.markdown("### 📄 Content Issues")
            content_issues = ats_results.get('content_issues', [])
            if content_issues and content_issues != ["analysis_failed"]:
                for i, issue in enumerate(content_issues, 1):
                    st.markdown(f"**{i}.** {issue}")
            else:
                st.success("✅ No content issues identified!")
        
        with col2:
            # ATS Optimization Tips
            st.markdown("### 💡 ATS Optimization Tips")
            optimization_tips = ats_results.get('ats_optimization_tips', [])
            if optimization_tips and optimization_tips != ["Please check your Google Gemini API key and ensure the service is available."]:
                for i, tip in enumerate(optimization_tips, 1):
                    st.markdown(f"**{i}.** {tip}")
            else:
                st.info("No optimization tips available at this time.")
            
            # Keyword Suggestions
            st.markdown("### 🔑 Keyword Suggestions")
            keyword_suggestions = ats_results.get('keyword_suggestions', [])
            if keyword_suggestions and keyword_suggestions != ["analysis_failed"]:
                for keyword in keyword_suggestions:
                    st.info(f"🔑 {keyword}")
            else:
                st.info("No keyword suggestions available.")
            
            # Structure Recommendations
            st.markdown("### 🏗️ Structure Recommendations")
            structure_recs = ats_results.get('structure_recommendations', [])
            if structure_recs and structure_recs != ["analysis_failed"]:
                for i, rec in enumerate(structure_recs, 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.info("No structure recommendations available.")
        
        # Download ATS Report
        st.divider()
        st.markdown("### 📥 Download ATS Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create ATS text report
            ats_report_text = f"""myAIHr - ATS Optimization Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ATS SCORES
==========
Overall ATS Score: {ats_results.get('ats_score', 0)}%
Keyword Match Score: {ats_results.get('keyword_match_score', 0)}%
Formatting Score: {ats_results.get('formatting_score', 0)}%
Content Score: {ats_results.get('content_score', 0)}%

SUMMARY
=======
{ats_results.get('summary', 'No summary available.')}

MISSING KEYWORDS
===============
{chr(10).join([f"• {keyword}" for keyword in ats_results.get('missing_keywords', [])])}

FORMATTING ISSUES
=================
{chr(10).join([f"• {issue}" for issue in ats_results.get('formatting_issues', [])])}

CONTENT ISSUES
==============
{chr(10).join([f"• {issue}" for issue in ats_results.get('content_issues', [])])}

ATS OPTIMIZATION TIPS
=====================
{chr(10).join([f"{i+1}. {tip}" for i, tip in enumerate(ats_results.get('ats_optimization_tips', []))])}

KEYWORD SUGGESTIONS
===================
{chr(10).join([f"• {keyword}" for keyword in ats_results.get('keyword_suggestions', [])])}

STRUCTURE RECOMMENDATIONS
=========================
{chr(10).join([f"{i+1}. {rec}" for i, rec in enumerate(ats_results.get('structure_recommendations', []))])}
"""
            
            st.download_button(
                label="📄 Download ATS Report (TXT)",
                data=ats_report_text,
                file_name=f"ats_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Create ATS markdown report
            ats_report_md = f"""# myAIHr - ATS Optimization Report
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## ATS Scores
- **Overall ATS Score:** {ats_results.get('ats_score', 0)}%
- **Keyword Match Score:** {ats_results.get('keyword_match_score', 0)}%
- **Formatting Score:** {ats_results.get('formatting_score', 0)}%
- **Content Score:** {ats_results.get('content_score', 0)}%

## Summary
{ats_results.get('summary', 'No summary available.')}

## Missing Keywords
{chr(10).join([f"- {keyword}" for keyword in ats_results.get('missing_keywords', [])])}

## Formatting Issues
{chr(10).join([f"- {issue}" for issue in ats_results.get('formatting_issues', [])])}

## Content Issues
{chr(10).join([f"- {issue}" for issue in ats_results.get('content_issues', [])])}

## ATS Optimization Tips
{chr(10).join([f"{i+1}. {tip}" for i, tip in enumerate(ats_results.get('ats_optimization_tips', []))])}

## Keyword Suggestions
{chr(10).join([f"- {keyword}" for keyword in ats_results.get('keyword_suggestions', [])])}

## Structure Recommendations
{chr(10).join([f"{i+1}. {rec}" for i, rec in enumerate(ats_results.get('structure_recommendations', []))])}
"""
            
            st.download_button(
                label="📝 Download ATS Report (MD)",
                data=ats_report_md,
                file_name=f"ats_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    else:
        st.markdown('<h2 class="section-header">🎯 ATS Optimization Analysis</h2>', unsafe_allow_html=True)
        st.info("📊 No analysis results available. Please run an analysis in the 'Upload & Analyze' tab first.")

# Tab 4: Cover Letter
with tab4:
    st.markdown('<h2 class="section-header">📝 Cover Letter Generator</h2>', unsafe_allow_html=True)
    
    if st.session_state.resume_text and st.session_state.job_text:
        # Cover Letter Settings
        col1, col2 = st.columns(2)
        
        with col1:
            tone = st.selectbox(
                "Select Tone",
                options=["formal", "confident", "enthusiastic"],
                index=0,
                help="Choose the tone for your cover letter"
            )
        
        with col2:
            generate_cover_letter_button = st.button(
                "🚀 Generate Cover Letter",
                use_container_width=True,
                type="primary"
            )
        
        # Generate cover letter
        if generate_cover_letter_button:
            if not gemini_api_key:
                st.error("❌ Google Gemini API key is required for cover letter generation.")
                st.info("💡 Please enter your API key in the sidebar to continue.")
            else:
                try:
                    with st.spinner("📝 Generating personalized cover letter..."):
                        cover_letter = generate_cover_letter(
                            st.session_state.resume_text,
                            st.session_state.job_text,
                            tone,
                            gemini_api_key
                        )
                        st.session_state.cover_letter = cover_letter
                    
                    st.success("✅ Cover letter generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Cover letter generation failed: {str(e)}")
                    st.info("💡 Please check your Google Gemini API key and try again.")
        
        # Display generated cover letter with editing capabilities
        if st.session_state.cover_letter:
            st.markdown("### 📄 Cover Letter Editor")
            
            # Editable cover letter text area
            edited_cover_letter = st.text_area(
                "Edit your cover letter",
                value=st.session_state.cover_letter,
                height=400,
                help="You can edit the generated cover letter here"
            )
            
            # Update session state with edited version
            if edited_cover_letter != st.session_state.cover_letter:
                st.session_state.cover_letter = edited_cover_letter
                st.success("✅ Cover letter updated!")
            
            st.divider()
            
            # Action buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("🔄 Regenerate with AI", use_container_width=True, type="secondary"):
                    if not gemini_api_key:
                        st.error("❌ Google Gemini API key is required.")
                    else:
                        try:
                            with st.spinner("🔄 Regenerating cover letter..."):
                                new_cover_letter = generate_cover_letter(
                                    st.session_state.resume_text,
                                    st.session_state.job_text,
                                    tone,
                                    gemini_api_key
                                )
                                st.session_state.cover_letter = new_cover_letter
                                st.success("✅ Cover letter regenerated!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Regeneration failed: {str(e)}")
            
            with col2:
                # Custom prompt regeneration
                custom_prompt = st.text_input(
                    "Custom instructions for regeneration",
                    placeholder="e.g., Make it more specific about my experience...",
                    help="Add custom instructions for AI regeneration"
                )
                
                if st.button("🤖 Regenerate with Custom Prompt", use_container_width=True, type="secondary"):
                    if not gemini_api_key:
                        st.error("❌ Google Gemini API key is required.")
                    elif not custom_prompt:
                        st.warning("⚠️ Please enter custom instructions.")
                    else:
                        try:
                            with st.spinner("🤖 Regenerating with custom instructions..."):
                                new_cover_letter = generate_cover_letter(
                                    st.session_state.resume_text,
                                    st.session_state.job_text,
                                    tone,
                                    gemini_api_key,
                                    custom_prompt
                                )
                                st.session_state.cover_letter = new_cover_letter
                                st.success("✅ Cover letter regenerated with custom instructions!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Custom regeneration failed: {str(e)}")
            
            with col3:
                # Download as TXT
                st.download_button(
                    label="📄 Download as TXT",
                    data=st.session_state.cover_letter,
                    file_name=f"cover_letter_{tone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col4:
                # Download as Markdown
                cover_letter_md = f"""# Cover Letter
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Tone: {tone.title()}*

{st.session_state.cover_letter}
"""
                st.download_button(
                    label="📝 Download as MD",
                    data=cover_letter_md,
                    file_name=f"cover_letter_{tone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col5:
                # Download as PDF
                pdf_buffer = generate_pdf(st.session_state.cover_letter, tone)
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"cover_letter_{tone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Additional features
            st.divider()
            st.markdown("### 💡 Tips for Better Cover Letters")
            st.markdown("""
            - **Customize the tone** based on the company culture
            - **Highlight specific achievements** from your resume
            - **Address key requirements** from the job description
            - **Keep it concise** (1-2 pages maximum)
            - **Proofread carefully** before sending
            """)
        
        else:
            st.info("📝 No cover letter generated yet. Click 'Generate Cover Letter' to create one.")
    
    else:
        st.error("❌ Resume and job description texts are required for cover letter generation.")
        st.info("💡 Please upload and extract text from your resume and job description in the 'Upload & Analyze' tab first.")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, Google Gemini • myAIHr") 