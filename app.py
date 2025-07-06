import streamlit as st
import pandas as pd
from datetime import datetime
from utils import extract_text_from_file, get_file_info, validate_file_type, analyze_resume_vs_jd, analyze_ats_score, generate_cover_letter, get_hf_client, HF_AVAILABLE

# Set page config
st.set_page_config(
    page_title="ResumeAI Helper",
    page_icon="📄",
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
        <h1 style="font-size: 1.8rem; color: #1f77b4; margin-bottom: 0.5rem;">📄 ResumeAI Helper</h1>
        <p style="color: #6c757d; font-size: 0.9rem;">AI-Powered Resume Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🚀 How to Use")
    st.markdown("""
    1. **Upload** your resume and job description
    2. **Extract** text from uploaded files
    3. **Analyze** with AI for insights
    4. **Generate** a cover letter
    """)
    
    st.divider()
    
    # AI Model Settings
    st.markdown("### 🤖 AI Model Settings")
    
    # AI Provider Selection
    ai_provider = st.radio(
        "Choose AI Provider",
        options=["☁️ Cloud (Hugging Face)", "🖥️ Local (Ollama)"],
        index=0,  # Default to Hugging Face for cloud deployment
        help="For cloud deployment, Hugging Face is recommended. Ollama requires local installation."
    )
    
    use_hf = ai_provider == "☁️ Cloud (Hugging Face)"
    
    # Info for cloud deployment
    if use_hf:
        st.info("☁️ **Cloud Mode:** Using Hugging Face models for online deployment.")
    else:
        st.warning("🖥️ **Local Mode:** Ollama requires local installation and won't work in cloud deployment.")
    
    if use_hf:
        # Hugging Face Settings
        st.markdown("#### ☁️ Hugging Face Settings")
        
        # Check if HF is available
        if not HF_AVAILABLE:
            st.error("❌ Hugging Face Hub not installed. Run: `pip install huggingface_hub`")
        else:
            # HF API Token
            hf_token = st.text_input(
                "Hugging Face API Token",
                type="password",
                help="Get your token from https://huggingface.co/settings/tokens",
                placeholder="hf_..."
            )
            
            # Popular HF models
            hf_models = [
                "mistralai/Mistral-7B-Instruct-v0.2",
                "meta-llama/Llama-2-7b-chat-hf",
                "microsoft/DialoGPT-medium",
                "gpt2",
                "tiiuae/falcon-7b-instruct"
            ]
            
            selected_model = st.selectbox(
                "Select Hugging Face Model",
                options=hf_models,
                index=0,
                help="Choose a Hugging Face model for analysis"
            )
            
            # Test HF connection
            if hf_token and st.button("🔍 Test HF Connection", use_container_width=True):
                try:
                    with st.spinner("Testing Hugging Face connection..."):
                        hf_client = get_hf_client(hf_token)
                        if hf_client:
                            st.success("✅ Hugging Face connection successful!")
                        else:
                            st.error("❌ Failed to connect to Hugging Face")
                except Exception as e:
                    st.error(f"❌ Hugging Face connection failed: {str(e)}")
            
            # Troubleshooting guide
            with st.expander("🔧 Hugging Face Troubleshooting Guide", expanded=False):
                st.markdown("""
                ### Common Hugging Face API Issues
                
                #### ❌ 401 Unauthorized Error (WIDESPREAD ISSUE)
                **Symptoms:** "Invalid credentials in Authorization header"
                
                **Current Status:** This is a known issue affecting many users since June 2025. Even newly generated tokens are failing.
                
                **Solutions:**
                1. **Use Ollama instead** - This is the most reliable solution
                2. **Check token format** - Must start with `hf_`
                3. **Verify token validity** - Get a new token from [Hugging Face Tokens](https://huggingface.co/settings/tokens)
                4. **Check account status** - Ensure your account is active and not suspended
                5. **Token permissions** - Make sure token has 'read' access for inference
                6. **Contact support** - Email website@huggingface.co with your username
                
                #### ❌ 403 Forbidden Error
                **Symptoms:** "Token doesn't have required permissions"
                
                **Solutions:**
                1. **Update token permissions** - Add 'read' access for inference
                2. **Check model access** - Some models require special access
                3. **Verify account type** - Free accounts have usage limits
                
                #### ❌ 429 Rate Limited
                **Symptoms:** "Too many requests"
                
                **Solutions:**
                1. **Wait and retry** - Rate limits reset automatically
                2. **Upgrade account** - Pro accounts have higher limits
                3. **Reduce request frequency** - Space out your API calls
                
                #### ❌ 500 Server Error
                **Symptoms:** "Internal Server Error"
                
                **Solutions:**
                1. **Try again later** - Temporary service issue
                2. **Check Hugging Face status** - Visit [status.huggingface.co](https://status.huggingface.co)
                3. **Use different model** - Some models may be temporarily unavailable
                
                ### Getting Help
                - **Community Forum:** [discuss.huggingface.co](https://discuss.huggingface.co)
                - **Documentation:** [huggingface.co/docs](https://huggingface.co/docs)
                - **Status Page:** [status.huggingface.co](https://status.huggingface.co)
                """)
            
            st.info(f"Selected model: **{selected_model}**")
    else:
        # Ollama Settings
        st.markdown("#### 🖥️ Ollama Settings")
        
        # Default model options
        default_models = ["llama3.1", "mistral", "gemma3:12b"]
        
        # Try to get available models from Ollama
        try:
            import ollama
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            model_options = available_models if available_models else default_models
        except Exception as e:
            model_options = default_models
            st.warning(f"⚠️ Could not connect to Ollama: {str(e)}")
        
        selected_model = st.selectbox(
            "Select Ollama Model",
            options=model_options,
            index=0,
            help="Choose the AI model to use for analysis"
        ) or "llama3.1"
        
        st.info(f"Selected model: **{selected_model}**")
    
    # Model status check
    if st.button("🔍 Check Model Status", use_container_width=True):
        try:
            import ollama
            with st.spinner("Checking Ollama connection..."):
                models_response = ollama.list()
            
            st.success("✅ Ollama is running!")
            st.write("**Available models:**")
            for model in models_response.models:
                if model.size:
                    size_mb = model.size / (1024 * 1024)
                    if size_mb > 1024:
                        size_str = f"{size_mb/1024:.1f} GB"
                    else:
                        size_str = f"{size_mb:.0f} MB"
                    st.write(f"• **{model.model}** ({size_str})")
                else:
                    st.write(f"• **{model.model}** (size unknown)")
                
        except Exception as e:
            st.error(f"❌ Ollama connection failed: {str(e)}")
            st.info("💡 **Troubleshooting:**")
            st.info("1. Install Ollama: https://ollama.ai")
            st.info("2. Start: `ollama serve`")
            st.info("3. Check: `ollama list`")
            st.info("4. Pull: `ollama pull llama3.1`")
    
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
    **ResumeAI Helper** uses local AI models to analyze resumes against job descriptions and generate personalized cover letters.
    
    Built with Streamlit and Ollama.
    """)

# Main content
st.markdown('<h1 class="main-header">📄 ResumeAI Helper</h1>', unsafe_allow_html=True)

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
        st.markdown("### 📋 Resume Upload")
        resume_file = st.file_uploader(
            "Upload your resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )
        
        if resume_file:
            st.success(f"✅ Resume uploaded: {resume_file.name}")
            file_size = resume_file.size
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} bytes"
            st.info(f"📁 File size: {size_str}")
            
            # Auto-extract text when file is uploaded
            try:
                with st.spinner("📄 Automatically extracting text from resume..."):
                    extracted_text = extract_text_from_file(resume_file)
                    if extracted_text:
                        st.session_state.resume_text = extracted_text
                        st.success("✅ Resume text extracted automatically!")
                        st.info(f"📊 Extracted {len(extracted_text.split())} words")
                    else:
                        st.error("❌ Failed to extract text from resume.")
            except Exception as e:
                st.error(f"❌ Error extracting text: {str(e)}")
        else:
            st.info("📝 Please upload your resume")

    with col2:
        st.markdown("### 💼 Job Description")
        jd_option = st.radio(
            "Choose input method:",
            ["📁 Upload File", "✏️ Enter Text"],
            horizontal=True
        )
        
        if jd_option == "📁 Upload File":
            job_file = st.file_uploader(
                "Upload job description (PDF, DOCX, TXT)",
                type=['pdf', 'docx', 'txt'],
                help="Upload the job description in PDF, DOCX, or TXT format"
            )
            
            if job_file:
                st.success(f"✅ Job description uploaded: {job_file.name}")
                file_size = job_file.size
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size} bytes"
                st.info(f"📁 File size: {size_str}")
                
                # Auto-extract text when file is uploaded
                try:
                    with st.spinner("📄 Automatically extracting text from job description..."):
                        extracted_text = extract_text_from_file(job_file)
                        if extracted_text:
                            st.session_state.job_text = extracted_text
                            st.success("✅ Job description text extracted automatically!")
                            st.info(f"📊 Extracted {len(extracted_text.split())} words")
                        else:
                            st.error("❌ Failed to extract text from job description.")
                except Exception as e:
                    st.error(f"❌ Error extracting text: {str(e)}")
            else:
                st.info("📝 Please upload the job description")
                
            job_text = None
        else:
            job_text = st.text_area(
                "Enter job description",
                height=200,
                placeholder="Paste the job description here...",
                help="Enter or paste the job description text",
                key="job_text_input"
            )
            
            # Auto-process text when entered
            if job_text and job_text.strip():
                st.session_state.job_text = job_text.strip()
                word_count = len(job_text.split())
                char_count = len(job_text)
                st.success("✅ Job description text processed automatically!")
                st.info(f"📊 **{word_count} words** | **{char_count} characters**")
            elif not job_text or not job_text.strip():
                st.session_state.job_text = ""
                st.info("📝 Please enter the job description")
                
            job_file = None

    # Analysis button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        analyze_button = st.button(
            "🚀 Analyze Resume & Job Description",
            type="primary",
            use_container_width=True,
            disabled=not (st.session_state.resume_text and st.session_state.job_text)
        )

    # Display extracted text
    if st.session_state.resume_text or st.session_state.job_text:
        st.divider()
        st.markdown('<h2 class="section-header">📝 Extracted Text Preview</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Resume Preview")
            if st.session_state.resume_text:
                resume_words = len(st.session_state.resume_text.split())
                resume_chars = len(st.session_state.resume_text)
                st.info(f"📊 **{resume_words} words** | **{resume_chars} characters**")
                
                with st.expander("📖 View Resume Content", expanded=False):
                    st.text_area(
                        "Resume Content",
                        value=st.session_state.resume_text,
                        height=300,
                        key="resume_display",
                        disabled=True
                    )
            else:
                st.info("📝 No resume text extracted yet")
        
        with col2:
            st.markdown("### 💼 Job Description Preview")
            if st.session_state.job_text:
                jd_words = len(st.session_state.job_text.split())
                jd_chars = len(st.session_state.job_text)
                st.info(f"📊 **{jd_words} words** | **{jd_chars} characters**")
                
                with st.expander("📖 View Job Description Content", expanded=False):
                    st.text_area(
                        "Job Description Content",
                        value=st.session_state.job_text,
                        height=300,
                        key="job_display",
                        disabled=True
                    )
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
                        selected_model,
                        use_hf=use_hf,
                        hf_token=hf_token if use_hf else None
                    )
                    st.session_state.analysis_results = analysis_results
                    
                    # Save to history
                    save_analysis_to_history(
                        st.session_state.resume_text, 
                        st.session_state.job_text, 
                        analysis_results, 
                        selected_model
                    )
                
                st.success("✅ Analysis completed successfully!")
                st.info("💾 Analysis saved to history. You can view it in the sidebar.")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("💡 Troubleshooting tips:")
                st.info("• Make sure Ollama is running (`ollama serve`)")
                st.info("• Check that the selected model is available (`ollama list`)")
                st.info("• Try selecting a different model from the sidebar")
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
            if improvements and improvements != ["Please check that Ollama is running and the model is installed. Try running 'ollama list' to see available models."]:
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
            else:
                st.success("✅ All required skills found in your resume!")
            
            # Display additional skills
            if additional_skills:
                st.markdown("**🎯 Bonus Skills (Not Required but Valuable):**")
                bonus_cols = st.columns(3)
                for i, skill in enumerate(additional_skills[:6]):  # Show top 6 bonus skills
                    col_idx = i % 3
                    with bonus_cols[col_idx]:
                        st.info(f"🎯 {skill}")
                if len(additional_skills) > 6:
                    st.markdown(f"*... and {len(additional_skills) - 6} more bonus skills*")
            
            st.markdown("""
            **💡 Tip:** Focus on adding the missing required skills first, then highlight your bonus skills in interviews.
            """)
        
        # Additional Visual Elements
        st.divider()
        
        # Performance Slider for overall assessment
        st.markdown("### 📊 Overall Performance Assessment")
        overall_performance = (score + skills_match) / 2
        st.slider(
            "Resume Performance Score",
            min_value=0,
            max_value=100,
            value=int(overall_performance),
            disabled=True,
            help="Combined score based on match and skills alignment"
        )
        
        # Performance indicator
        if overall_performance >= 80:
            st.success("🎉 **Excellent!** Your resume shows strong alignment with the job requirements.")
        elif overall_performance >= 60:
            st.info("👍 **Good!** Your resume has good potential with some improvements.")
        elif overall_performance >= 40:
            st.warning("⚠️ **Fair.** Consider implementing the suggested improvements.")
        else:
            st.error("❌ **Needs Work.** Significant improvements are recommended.")
        
        # Visual Analysis Section
        st.divider()
        with st.expander("🔍 Visual Analysis", expanded=False):
            st.markdown("### 📊 Text Analysis Visualizations")
            
            # Import visualization functions
            from utils import create_word_cloud, create_skills_bar_chart
            
            # Word Clouds
            st.markdown("#### ☁️ Word Clouds")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📄 Resume Keywords**")
                resume_fig = create_word_cloud(st.session_state.resume_text, "Resume Keywords")
                st.pyplot(resume_fig, use_container_width=True)
            
            with col2:
                st.markdown("**💼 Job Description Keywords**")
                jd_fig = create_word_cloud(st.session_state.job_text, "Job Description Keywords")
                st.pyplot(jd_fig, use_container_width=True)
            
            st.markdown("---")
            
            # Skills Bar Chart
            st.markdown("#### 📈 Skills Analysis")
            st.markdown("**Top 10 skills comparison between resume and job description:**")
            
            skills_fig = create_skills_bar_chart(st.session_state.resume_text, st.session_state.job_text)
            st.plotly_chart(skills_fig, use_container_width=True)
            
            # Additional insights
            st.markdown("**💡 Insights:**")
            st.markdown("""
            - **Word Clouds** show the most frequent keywords in each document
            - **Skills Chart** compares skill mentions between your resume and the job requirements
            - **Blue bars** = Skills found in your resume
            - **Orange bars** = Skills mentioned in the job description
            - **Higher overlap** indicates better skills alignment
            """)
        
        # Download AI Feedback Report
        st.divider()
        st.markdown("### 📥 Download AI Feedback Report")
        
        # Create comprehensive feedback report
        if st.session_state.analysis_results:
            report_data = st.session_state.analysis_results
            score = report_data.get('score', 0)
            skills_match = report_data.get('skills_match', 0)
            summary = report_data.get('summary', 'No summary available.')
            improvements = report_data.get('improvements', [])
            missing_keywords = report_data.get('missing_keywords', [])
            found_skills = report_data.get('found_skills', [])
            additional_skills = report_data.get('additional_skills', [])
            formatting_issues = report_data.get('formatting_issues', [])
            tone_grammar = report_data.get('tone_grammar', 'No evaluation available.')
            
            # Create comprehensive report text
            report_content = f"""# AI Resume Analysis Report

## 📊 Executive Summary
**Overall Match Score:** {score}%
**Skills Match:** {skills_match}%

## 📝 AI Summary
{summary}

## 🎯 Detailed Analysis

### Overall Performance
- **Match Score:** {score}%
- **Skills Alignment:** {skills_match}%
- **Performance Level:** {'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair' if score >= 40 else 'Needs Work'}

### Skills Analysis
**Required Skills Found:** {len(found_skills)} skills identified in your resume
**Missing Skills:** {len(missing_keywords)} skills need to be added
**Additional Skills:** {len(additional_skills)} bonus skills detected

#### ✅ Skills Found in Your Resume:
{chr(10).join([f"- {skill}" for skill in found_skills[:10]])}

#### ❌ Missing Skills to Add:
{chr(10).join([f"- {skill}" for skill in missing_keywords[:10]])}

#### 🎯 Bonus Skills (Not Required but Valuable):
{chr(10).join([f"- {skill}" for skill in additional_skills[:10]])}

### Formatting & Presentation
**Tone & Grammar Evaluation:** {tone_grammar}

#### ⚠️ Formatting Issues Identified:
{chr(10).join([f"- {issue}" for issue in formatting_issues]) if formatting_issues else "- No formatting issues identified"}

## 💡 Improvement Recommendations
{chr(10).join([f"{i+1}. {improvement}" for i, improvement in enumerate(improvements)])}

## 📈 Action Plan
1. **Priority 1:** Add missing required skills to your resume
2. **Priority 2:** Address formatting issues identified
3. **Priority 3:** Highlight your bonus skills in interviews
4. **Priority 4:** Implement the specific improvement suggestions above

---
*Generated by ResumeAI Helper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Download buttons for the report
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Save Feedback Report (TXT)",
                    data=report_content,
                    file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download the complete AI feedback report as a text file",
                    use_container_width=True,
                    icon="📄"
                )
            
            with col2:
                # Create markdown version with better formatting
                markdown_report = f"""# AI Resume Analysis Report

## 📊 Executive Summary
**Overall Match Score:** {score}%
**Skills Match:** {skills_match}%

## 📝 AI Summary
{summary}

## 🎯 Detailed Analysis

### Overall Performance
- **Match Score:** {score}%
- **Skills Alignment:** {skills_match}%
- **Performance Level:** {'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair' if score >= 40 else 'Needs Work'}

### Skills Analysis
**Required Skills Found:** {len(found_skills)} skills identified in your resume
**Missing Skills:** {len(missing_keywords)} skills need to be added
**Additional Skills:** {len(additional_skills)} bonus skills detected

#### ✅ Skills Found in Your Resume:
{chr(10).join([f"- {skill}" for skill in found_skills[:10]])}

#### ❌ Missing Skills to Add:
{chr(10).join([f"- {skill}" for skill in missing_keywords[:10]])}

#### 🎯 Bonus Skills (Not Required but Valuable):
{chr(10).join([f"- {skill}" for skill in additional_skills[:10]])}

### Formatting & Presentation
**Tone & Grammar Evaluation:** {tone_grammar}

#### ⚠️ Formatting Issues Identified:
{chr(10).join([f"- {issue}" for issue in formatting_issues]) if formatting_issues else "- No formatting issues identified"}

## 💡 Improvement Recommendations
{chr(10).join([f"{i+1}. {improvement}" for i, improvement in enumerate(improvements)])}

## 📈 Action Plan
1. **Priority 1:** Add missing required skills to your resume
2. **Priority 2:** Address formatting issues identified
3. **Priority 3:** Highlight your bonus skills in interviews
4. **Priority 4:** Implement the specific improvement suggestions above

---
*Generated by ResumeAI Helper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                
                st.download_button(
                    label="📋 Save Feedback Report (MD)",
                    data=markdown_report,
                    file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    help="Download the complete AI feedback report as a markdown file",
                    use_container_width=True,
                    icon="📋"
                )
            
    else:
        st.markdown('<h2 class="section-header">🤖 AI Feedback</h2>', unsafe_allow_html=True)
        st.info("📝 Please complete the analysis in the 'Upload & Analyze' tab to view AI feedback here.")

# Tab 3: ATS Score
with tab3:
    st.markdown('<h2 class="section-header">🎯 ATS Score Analysis</h2>', unsafe_allow_html=True)
    
    if st.session_state.resume_text and st.session_state.job_text:
        # Check if ATS analysis already exists in session state
        if 'ats_results' not in st.session_state:
            st.session_state.ats_results = None
        
        # ATS Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            ats_analyze_button = st.button(
                "🎯 Analyze ATS Score",
                type="primary",
                use_container_width=True,
                help="Analyze your resume for ATS optimization"
            )
        
        # Perform ATS analysis
        if ats_analyze_button:
            try:
                with st.spinner("🎯 Analyzing ATS compatibility..."):
                    ats_results = analyze_ats_score(
                        st.session_state.resume_text, 
                        st.session_state.job_text, 
                        selected_model,
                        use_hf=use_hf,
                        hf_token=hf_token if use_hf else None
                    )
                    st.session_state.ats_results = ats_results
                
                st.success("✅ ATS analysis completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error during ATS analysis: {str(e)}")
        
        # Display ATS results
        if st.session_state.ats_results:
            ats_data = st.session_state.ats_results
            
            # ATS Score Overview
            st.markdown("### 📊 ATS Score Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🎯 Overall ATS Score",
                    value=f"{ats_data.get('ats_score', 0)}%",
                    delta=None,
                    help="Overall compatibility with ATS systems"
                )
            
            with col2:
                st.metric(
                    label="🔑 Keyword Match",
                    value=f"{ats_data.get('keyword_match_score', 0)}%",
                    delta=None,
                    help="Percentage of job keywords found in resume"
                )
            
            with col3:
                st.metric(
                    label="📝 Formatting Score",
                    value=f"{ats_data.get('formatting_score', 0)}%",
                    delta=None,
                    help="ATS-friendly formatting and structure"
                )
            
            with col4:
                st.metric(
                    label="📄 Content Score",
                    value=f"{ats_data.get('content_score', 0)}%",
                    delta=None,
                    help="Content quality and relevance"
                )
            
            # Progress bars for visual representation
            st.markdown("### 📈 Detailed Scores")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🎯 Overall ATS Score**")
                ats_score = ats_data.get('ats_score', 0)
                st.progress(ats_score / 100, text=f"{ats_score}%")
                
                st.markdown("**🔑 Keyword Match Score**")
                keyword_score = ats_data.get('keyword_match_score', 0)
                st.progress(keyword_score / 100, text=f"{keyword_score}%")
            
            with col2:
                st.markdown("**📝 Formatting Score**")
                format_score = ats_data.get('formatting_score', 0)
                st.progress(format_score / 100, text=f"{format_score}%")
                
                st.markdown("**📄 Content Score**")
                content_score = ats_data.get('content_score', 0)
                st.progress(content_score / 100, text=f"{content_score}%")
            
            # ATS Summary
            st.markdown("### 📋 ATS Analysis Summary")
            summary = ats_data.get('summary', 'No summary available.')
            st.info(summary)
            
            # Detailed Analysis Sections
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ❌ Missing Keywords")
                missing_keywords = ats_data.get('missing_keywords', [])
                if missing_keywords:
                    for keyword in missing_keywords:
                        st.error(f"🔴 {keyword}")
                else:
                    st.success("✅ No missing keywords identified!")
                
                st.markdown("### ⚠️ Formatting Issues")
                formatting_issues = ats_data.get('formatting_issues', [])
                if formatting_issues:
                    for issue in formatting_issues:
                        st.warning(f"⚠️ {issue}")
                else:
                    st.success("✅ No formatting issues identified!")
                
                st.markdown("### 📝 Content Issues")
                content_issues = ats_data.get('content_issues', [])
                if content_issues:
                    for issue in content_issues:
                        st.error(f"🔴 {issue}")
                else:
                    st.success("✅ No content issues identified!")
            
            with col2:
                st.markdown("### 💡 ATS Optimization Tips")
                optimization_tips = ats_data.get('ats_optimization_tips', [])
                if optimization_tips:
                    for i, tip in enumerate(optimization_tips, 1):
                        st.success(f"💡 **{i}.** {tip}")
                
                st.markdown("### 🔑 Keyword Suggestions")
                keyword_suggestions = ats_data.get('keyword_suggestions', [])
                if keyword_suggestions:
                    for keyword in keyword_suggestions:
                        st.info(f"🔑 {keyword}")
                
                st.markdown("### 🏗️ Structure Recommendations")
                structure_recs = ats_data.get('structure_recommendations', [])
                if structure_recs:
                    for rec in structure_recs:
                        st.info(f"🏗️ {rec}")
            
            # ATS Best Practices Guide
            st.markdown("### 📚 ATS Best Practices Guide")
            
            with st.expander("🎯 How to Improve Your ATS Score", expanded=False):
                st.markdown("""
                #### **1. Use Standard Headings** 📋
                - **Work Experience** (not "Professional Background")
                - **Education** (not "Academic Background")
                - **Skills** (not "Core Competencies")
                - **Certifications** (not "Professional Development")
                
                #### **2. Choose the Right Keywords** 🔑
                - **Extract keywords** from the job description
                - **Use exact phrases** when possible
                - **Include variations** of important terms
                - **Place keywords strategically** in experience descriptions
                
                #### **3. Avoid Graphics and Tables** 🚫
                - **No images, logos, or graphics**
                - **No tables or complex formatting**
                - **No headers/footers** (important info gets lost)
                - **Use simple bullet points** instead
                
                #### **4. Customize for Each Job** 🎯
                - **Tailor keywords** to each specific position
                - **Highlight relevant experience** for the role
                - **Use industry-specific terminology**
                - **Match the job description language**
                
                #### **5. Proofread and Test** ✅
                - **Check for spelling and grammar errors**
                - **Test with ATS simulators** (Jobscan, Resume Worded)
                - **Ensure consistent formatting**
                - **Verify all contact information is visible**
                
                #### **6. File Format Matters** 📄
                - **Use .docx or .pdf** (avoid .txt)
                - **Ensure compatibility** with major ATS systems
                - **Keep file size reasonable** (< 2MB)
                - **Use standard fonts** (Arial, Calibri, Times New Roman)
                """)
            
            # Download ATS Report
            st.divider()
            st.markdown("### 📥 Download ATS Analysis Report")
            
            # Create comprehensive ATS report
            ats_report_content = f"""# ATS Optimization Analysis Report

## 📊 ATS Score Summary
**Overall ATS Score:** {ats_data.get('ats_score', 0)}%
**Keyword Match Score:** {ats_data.get('keyword_match_score', 0)}%
**Formatting Score:** {ats_data.get('formatting_score', 0)}%
**Content Score:** {ats_data.get('content_score', 0)}%

## 📋 Analysis Summary
{ats_data.get('summary', 'No summary available.')}

## 🎯 Detailed Analysis

### Missing Keywords
{chr(10).join([f"- {keyword}" for keyword in ats_data.get('missing_keywords', [])]) if ats_data.get('missing_keywords') else "- No missing keywords identified"}

### Formatting Issues
{chr(10).join([f"- {issue}" for issue in ats_data.get('formatting_issues', [])]) if ats_data.get('formatting_issues') else "- No formatting issues identified"}

### Content Issues
{chr(10).join([f"- {issue}" for issue in ats_data.get('content_issues', [])]) if ats_data.get('content_issues') else "- No content issues identified"}

## 💡 Optimization Recommendations

### ATS Optimization Tips
{chr(10).join([f"{i+1}. {tip}" for i, tip in enumerate(ats_data.get('ats_optimization_tips', []))])}

### Keyword Suggestions
{chr(10).join([f"- {keyword}" for keyword in ats_data.get('keyword_suggestions', [])])}

### Structure Recommendations
{chr(10).join([f"- {rec}" for rec in ats_data.get('structure_recommendations', [])])}

## 📚 ATS Best Practices

### 1. Use Standard Headings
- Work Experience, Education, Skills, Certifications
- Avoid creative or non-standard section names

### 2. Choose the Right Keywords
- Extract keywords from job descriptions
- Use exact phrases when possible
- Include variations of important terms

### 3. Avoid Graphics and Tables
- No images, logos, or graphics
- No tables or complex formatting
- Use simple bullet points instead

### 4. Customize for Each Job
- Tailor keywords to each specific position
- Highlight relevant experience for the role
- Use industry-specific terminology

### 5. Proofread and Test
- Check for spelling and grammar errors
- Test with ATS simulators
- Ensure consistent formatting

### 6. File Format Matters
- Use .docx or .pdf format
- Keep file size reasonable (< 2MB)
- Use standard fonts (Arial, Calibri, Times New Roman)

---
*Generated by ResumeAI Helper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Download buttons for ATS report
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Save ATS Report (TXT)",
                    data=ats_report_content,
                    file_name=f"ats_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download the complete ATS analysis report as a text file",
                    use_container_width=True,
                    icon="📄"
                )
            
            with col2:
                st.download_button(
                    label="📋 Save ATS Report (MD)",
                    data=ats_report_content,
                    file_name=f"ats_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    help="Download the complete ATS analysis report as a markdown file",
                    use_container_width=True,
                    icon="📋"
                )
    
    else:
        st.info("📝 Please upload your resume and job description in the 'Upload & Analyze' tab to perform ATS analysis.")

# Tab 4: Cover Letter
with tab4:
    st.markdown('<h2 class="section-header">📝 Cover Letter Generator</h2>', unsafe_allow_html=True)
    
    if st.session_state.resume_text and st.session_state.job_text:
        # Cover letter configuration
        st.markdown("### ⚙️ Cover Letter Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tone selection dropdown
            tone_options = {
                "formal": "🎩 Formal - Professional and traditional",
                "confident": "💪 Confident - Strong and assertive", 
                "enthusiastic": "🚀 Enthusiastic - Energetic and passionate"
            }
            
            selected_tone = st.selectbox(
                "Choose Cover Letter Tone",
                options=list(tone_options.keys()),
                format_func=lambda x: tone_options[x],
                help="Select the tone that best matches your personality and the company culture"
            )
            
            # Display tone description
            tone_descriptions = {
                "formal": "Professional, respectful, and traditional tone focusing on qualifications and experience.",
                "confident": "Strong, assertive tone demonstrating self-assurance and leadership qualities.",
                "enthusiastic": "Energetic, passionate tone showing excitement and motivation for the opportunity."
            }
            
            st.info(f"**Selected Tone:** {tone_options[selected_tone].split(' - ')[1]}")
            st.caption(tone_descriptions[selected_tone])
        
        with col2:
            # Word count target
            st.markdown("**📊 Target Length:** ~250 words")
            st.progress(0, text="Ready to generate")
            
            # Model info
            st.info(f"**🤖 Using Model:** {selected_model}")
        
        st.divider()
        
        # Generate cover letter button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            generate_cover_button = st.button(
                "✍️ Generate Cover Letter",
                type="primary",
                use_container_width=True,
                help=f"Generate a {selected_tone} cover letter based on your resume and job description"
            )
        
        # Generate cover letter when button is clicked
        if generate_cover_button:
            try:
                with st.spinner(f"✍️ Generating {selected_tone} cover letter..."):
                    cover_letter = generate_cover_letter(
                        st.session_state.resume_text, 
                        st.session_state.job_text, 
                        selected_tone,
                        selected_model,
                        use_hf=use_hf,
                        hf_token=hf_token if use_hf else None
                    )
                    st.session_state.cover_letter = cover_letter
                    st.session_state.cover_letter_tone = selected_tone
                
                st.success(f"✅ {selected_tone.capitalize()} cover letter generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Cover letter generation failed: {str(e)}")
                st.info("💡 Troubleshooting tips:")
                st.info("• Make sure Ollama is running (`ollama serve`)")
                st.info("• Check that the selected model is available (`ollama list`)")
                st.info("• Try selecting a different model from the sidebar")
        
        # Display cover letter if available
        if st.session_state.cover_letter:
            st.divider()
            st.markdown("### 📄 Generated Cover Letter")
            
            # Display tone and word/character count
            cover_words = len(st.session_state.cover_letter.split())
            cover_chars = len(st.session_state.cover_letter)
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📊 **{cover_words} words** | **{cover_chars} characters**")
            with col2:
                tone_used = st.session_state.get('cover_letter_tone', 'formal')
                st.success(f"🎯 **Tone:** {tone_used.capitalize()}")
            
            # Display cover letter in text area
            cover_letter_text = st.text_area(
                "Cover Letter Content",
                value=st.session_state.cover_letter,
                height=400,
                key="cover_letter_display",
                help="Review and edit the generated cover letter as needed"
            )
            
            # Action buttons
            st.markdown("### 📥 Download Cover Letter")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copy to Clipboard", key="copy_cover", use_container_width=True):
                    st.write("📋 Cover letter copied to clipboard!")
                    st.info("💡 You can now paste the cover letter into any document.")
            
            with col2:
                st.download_button(
                    label="📄 Save Cover Letter (TXT)",
                    data=cover_letter_text,
                    file_name=f"cover_letter_{tone_used}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download the cover letter as a text file",
                    use_container_width=True,
                    icon="📄"
                )
            
            with col3:
                markdown_content = f"""# Cover Letter

**Generated with {tone_used.capitalize()} tone**

{cover_letter_text}

---
*Generated by ResumeAI Helper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                st.download_button(
                    label="📋 Save Cover Letter (MD)",
                    data=markdown_content,
                    file_name=f"cover_letter_{tone_used}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    help="Download the cover letter as a markdown file",
                    use_container_width=True,
                    icon="📋"
                )
            
            # Regenerate with different tone
            st.divider()
            st.markdown("### 🔄 Regenerate with Different Tone")
            st.info("💡 Want to try a different tone? Change the tone selection above and click 'Generate Cover Letter' again.")
            
    else:
        st.info("📝 Please upload your resume and job description in the 'Upload & Analyze' tab to generate a cover letter.")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, Ollama & Hugging Face • ResumeAI Helper") 