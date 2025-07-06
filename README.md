---
title: Resume & Job Description Analyzer
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Resume & Job Description Analyzer

A Streamlit web application for analyzing resumes against job descriptions using local AI models via Ollama.

## Features

- 📄 **File Upload Support**: Upload resumes and job descriptions in PDF, DOCX, or TXT formats
- 📝 **Text Input**: Option to enter job description text directly
- 🤖 **Dual AI Support**: Choose between local Ollama models or cloud-based Hugging Face models
- 🎯 **ATS Score Analysis**: Detailed ATS optimization analysis with improvement recommendations
- 📊 **Interactive Dashboard**: Visual metrics and detailed breakdowns
- 🎯 **Smart Recommendations**: Personalized suggestions for resume improvement
- 📝 **Cover Letter Generation**: Generate personalized cover letters with different tones
- 📊 **Visualizations**: Word clouds and skills comparison charts
- 💾 **Session History**: Save and review previous analyses
- 📥 **Download Reports**: Export analysis results, ATS reports, and cover letters
- 🔒 **Privacy Options**: Use local models for privacy or cloud models for convenience

## Setup

### Local Development

- Python 3.8 or higher
- pip (Python package installer)
- Ollama installed and running (see [Ollama Installation Guide](https://ollama.ai)) - **OR** - Hugging Face API token (see [Hugging Face Tokens](https://huggingface.co/settings/tokens))

### Cloud Deployment

- Hugging Face account
- Git installed
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

### Installation

1. **Clone or download this project**

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Choose your AI provider**:
   
   **Option A: Local Ollama (Privacy-focused)**
   ```bash
   # Download and install Ollama from https://ollama.ai
   # Then pull a model (e.g., llama3.2):
   ollama pull llama3.2
   ```
   
   **Option B: Cloud Hugging Face (Convenience-focused)**
   - Get your API token from [Hugging Face Tokens](https://huggingface.co/settings/tokens)
   - No local installation required

## Running the Application

1. **Activate the virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## Usage

1. **Choose AI Provider**: Select between local Ollama models or cloud-based Hugging Face models
2. **Configure API**: For Hugging Face, enter your API token; for Ollama, ensure it's running locally
3. **Select Model**: Choose your preferred AI model from the available options
4. **Upload Resume**: Use the file uploader to upload your resume (PDF, DOCX, or TXT)
5. **Add Job Description**: Either upload a job description file or enter the text directly
6. **Analyze**: Click the "Analyze" button to process the documents
7. **Review Results**: Explore the analysis results, metrics, and recommendations
8. **ATS Score Analysis**: Use the ATS Score tab to get detailed optimization recommendations
9. **Generate Cover Letter**: Create personalized cover letters with different tones
10. **Download Reports**: Export analysis results, ATS reports, and cover letters

## Project Structure

```
ResumeAI-Helper/
├── app.py              # Main Streamlit application
├── utils.py            # Utility functions for text extraction and AI analysis
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration for deployment
├── .dockerignore       # Docker ignore rules
├── deploy.sh           # Automated deployment script
├── DEPLOYMENT.md       # Detailed deployment instructions
├── README.md          # Project documentation
└── venv/              # Virtual environment (created during setup)
```

## Development

This application supports both local and cloud-based AI models. To extend it:

- Add support for more Ollama models
- Implement batch processing for multiple resumes
- Add database storage for analysis history
- Implement user authentication and session management
- Add export functionality for analysis reports

## Troubleshooting

### Hugging Face API Issues

If you encounter problems with Hugging Face API:

1. **Run diagnostics script:**
   ```bash
   python hf_diagnostics.py
   ```

2. **Common issues and solutions:**
   - **401 Unauthorized**: Check token format (must start with `hf_`) and validity
   - **403 Forbidden**: Ensure token has 'read' permissions for inference
   - **429 Rate Limited**: Wait and retry, or upgrade to Pro account
   - **500 Server Error**: Check [Hugging Face status](https://status.huggingface.co)

3. **Get help:**
   - [Hugging Face Community Forum](https://discuss.huggingface.co)
   - [Hugging Face Documentation](https://huggingface.co/docs)
   - [Service Status Page](https://status.huggingface.co)

## Technologies Used

- **Streamlit**: Web application framework
- **Ollama**: Local AI model inference
- **Hugging Face Hub**: Cloud-based AI model inference
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX text extraction
- **Pandas**: Data manipulation and analysis

## License

This project is open source and available under the MIT License. 