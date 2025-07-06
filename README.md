---
title: Resume & Job Description Analyzer
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 📄 ResumeAI Helper

An AI-powered resume analysis and cover letter generation tool built with Streamlit and Google Gemini.

## 🚀 Features

- **📤 File Upload**: Support for PDF, DOCX, and TXT files
- **🤖 AI Analysis**: Comprehensive resume vs job description analysis using Google Gemini
- **🎯 ATS Optimization**: Detailed ATS score analysis and improvement recommendations
- **📝 Cover Letter Generation**: AI-powered cover letter generation with tone selection
- **📊 Visualizations**: Word clouds and skills analysis charts
- **📥 Download Reports**: Export analysis results and cover letters in multiple formats
- **📚 Analysis History**: Save and revisit previous analyses

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ResumeAI-Helper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key (starts with "AIza...")

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`

3. **Configure Google Gemini**
   - Enter your Google Gemini API key in the sidebar
   - The app will validate the key automatically

4. **Upload Documents**
   - Upload your resume (PDF, DOCX, TXT)
   - Upload job description or enter text directly
   - Extract text from uploaded files

5. **Run Analysis**
   - Click "Analyze Resume vs Job Description"
   - View comprehensive AI feedback
   - Check ATS optimization scores
   - Generate personalized cover letters

## 📋 Features Overview

### 🤖 AI Analysis
- **Overall Match Score**: Percentage match between resume and job description
- **Skills Analysis**: Detailed breakdown of found, missing, and additional skills
- **Keyword Matching**: Identifies missing important keywords
- **Formatting Issues**: Points out potential formatting problems
- **Improvement Recommendations**: Actionable suggestions for improvement

### 🎯 ATS Optimization
- **ATS Score**: Overall compatibility with Applicant Tracking Systems
- **Keyword Match Score**: Percentage of job keywords found in resume
- **Formatting Score**: ATS-friendly formatting assessment
- **Content Score**: Content quality and relevance evaluation
- **Optimization Tips**: Specific actions to improve ATS performance

### 📝 Cover Letter Generation
- **Tone Selection**: Choose from formal, confident, or enthusiastic tones
- **Personalized Content**: AI-generated content based on your resume and job description
- **Download Options**: Export as TXT or Markdown files
- **Copy to Clipboard**: Easy copying for immediate use

### 📊 Visualizations
- **Word Clouds**: Visual representation of keywords in resume and job description
- **Skills Bar Chart**: Comparison of skills between resume and job description
- **Progress Bars**: Visual representation of scores and metrics

### 📚 Analysis History
- **Save Analyses**: Automatically saves each analysis to session history
- **Load Previous**: Revisit and compare previous analyses
- **Re-run Analysis**: Update analysis with new data
- **Clear History**: Manage saved analyses

## 🔧 Configuration

### Google Gemini API Key
The app requires a Google Gemini API key for AI features:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Enter the key in the app sidebar
4. The key is used locally and not stored permanently

### Supported File Formats
- **Resume**: PDF, DOCX, TXT
- **Job Description**: PDF, DOCX, TXT (or direct text input)

## 📁 Project Structure

```
ResumeAI-Helper/
├── app.py                 # Main Streamlit application
├── utils.py               # Utility functions and AI integration
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── Dockerfile            # Docker configuration
├── .dockerignore         # Docker ignore file
├── .gitignore           # Git ignore file
└── venv/                # Virtual environment (not in repo)
```

## 🐳 Docker Deployment

### Build and Run with Docker

1. **Build the Docker image**
   ```bash
   docker build -t resumeai-helper .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 resumeai-helper
   ```

3. **Access the application**
   - Open `http://localhost:8501` in your browser

### Environment Variables
You can set the Google Gemini API key as an environment variable:
```bash
docker run -p 8501:8501 -e GEMINI_API_KEY=your_api_key_here resumeai-helper
```

## 🚀 Deployment Options

### 🎯 Streamlit Community Cloud (Recommended)
**Easiest deployment option for Streamlit apps**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `ResumeAI-Helper`
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (Optional)
   - In your Streamlit app dashboard, go to "Settings" → "Secrets"
   - Add your Google Gemini API key:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```

4. **Access Your App**
   - Your app will be available at: `https://your-app-name.streamlit.app`
   - Automatic updates when you push to GitHub

**Benefits:**
- ✅ One-click deployment
- ✅ Automatic dependency management
- ✅ Free hosting
- ✅ Custom subdomain
- ✅ Direct GitHub integration
- ✅ No Docker configuration needed

### Local Development
- Run directly with Streamlit for development and testing
- Full access to all features
- Requires local Python environment

### Docker Deployment
- Containerized deployment for production
- Consistent environment across platforms
- Easy deployment to cloud platforms

### Other Cloud Platforms
The app can also be deployed to:
- **Heroku**: Using Docker deployment
- **Google Cloud Run**: Container-based deployment
- **AWS ECS**: Container orchestration
- **Azure Container Instances**: Cloud container service

## 🔒 Security and Privacy

- **Local Processing**: All file processing happens locally
- **API Key Security**: Google Gemini API key is used only for AI requests
- **No Data Storage**: Files and analysis results are not permanently stored
- **Session-based**: Data is only stored in browser session

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web app framework
- **Google Gemini**: For powerful AI capabilities
- **PyMuPDF**: For PDF text extraction
- **python-docx**: For DOCX file processing
- **Plotly**: For interactive visualizations
- **WordCloud**: For keyword visualization

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section in the app
2. Review the Google Gemini API documentation
3. Open an issue on GitHub
4. Check the app's built-in help and guidance

## 🔄 Updates

Stay updated with the latest features and improvements:
- Watch the repository for updates
- Check the changelog for version history
- Follow the project for announcements

---

**Built with ❤️ using Streamlit and Google Gemini** 