# 🚀 Deploying ResumeAI-Helper

This guide will help you deploy your ResumeAI-Helper app to various cloud platforms.

## 📋 Prerequisites

1. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Git**: Make sure you have Git installed
3. **Docker** (optional): For containerized deployment

## 🐳 Docker Deployment

### Local Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t resumeai-helper .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 -e GEMINI_API_KEY=your_api_key_here resumeai-helper
   ```

3. **Access the application**
   - Open `http://localhost:8501` in your browser

## ☁️ Cloud Platform Deployment

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the path to `app.py`
   - Add your Google Gemini API key as a secret

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to "Secrets"
   - Add: `GEMINI_API_KEY = "your_api_key_here"`

### Option 2: Hugging Face Spaces

1. **Create a Space**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Docker" SDK
   - Set hardware to "CPU" (free tier)

2. **Configure Environment Variables**
   - In Space settings, add: `GEMINI_API_KEY`
   - Value: Your Google Gemini API key

3. **Deploy**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/resume-ai-helper
   cd resume-ai-helper
   # Copy your app files
   git add .
   git commit -m "Initial deployment"
   git push
   ```

### Option 3: Google Cloud Run

1. **Enable Cloud Run API**
   ```bash
   gcloud services enable run.googleapis.com
   ```

2. **Build and deploy**
   ```bash
   gcloud run deploy resumeai-helper \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your_api_key_here
   ```

### Option 4: Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key_here
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## 🔧 Configuration

### Environment Variables

Set these in your deployment platform:

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `STREAMLIT_SERVER_PORT`: 8501 (default)
- `STREAMLIT_SERVER_ADDRESS`: 0.0.0.0 (default)

### Google Gemini API Key Setup

1. **Get API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key (starts with "AIza...")

2. **Set in Deployment**
   - Add as environment variable: `GEMINI_API_KEY`
   - Or add to Streamlit secrets for Streamlit Cloud

## 🌐 Accessing Your App

### Streamlit Cloud
```
https://your-app-name.streamlit.app
```

### Hugging Face Spaces
```
https://YOUR_USERNAME-resume-ai-helper.hf.space
```

### Google Cloud Run
```
https://resumeai-helper-xxxxx-uc.a.run.app
```

### Heroku
```
https://your-app-name.herokuapp.com
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check build logs
   - Ensure all dependencies are in `requirements.txt`
   - Verify Dockerfile syntax

2. **App Won't Start**
   - Check if port 8501 is exposed
   - Verify Streamlit command in Dockerfile
   - Check environment variables

3. **Google Gemini API Errors**
   - Verify your API key is correct
   - Check API key permissions
   - Ensure you have sufficient quota

4. **Memory Issues**
   - Upgrade to paid tier for more resources
   - Optimize your app code
   - Use smaller file uploads

### Getting Help

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Google Gemini Documentation**: [ai.google.dev](https://ai.google.dev)
- **Docker Documentation**: [docs.docker.com](https://docs.docker.com)

## 🎯 Next Steps

After successful deployment:

1. **Test your app** thoroughly
2. **Share the URL** with others
3. **Monitor usage** and performance
4. **Update regularly** with new features

## 📝 Notes

- **Free tier limits**: Vary by platform
- **Auto-sleep**: Some platforms sleep after inactivity
- **Custom domains**: Available with paid plans
- **Collaboration**: Most platforms support team collaboration

## 🔒 Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Environment Variables**: Use platform secrets/environment variables
- **HTTPS**: All major platforms provide HTTPS by default
- **Access Control**: Configure appropriate access controls

---

**Happy Deploying! 🚀** 