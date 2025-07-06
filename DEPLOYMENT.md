# 🚀 Deploying ResumeAI-Helper to Hugging Face Spaces

This guide will help you deploy your ResumeAI-Helper app to Hugging Face Spaces for free online access.

## 📋 Prerequisites

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)
2. **Git**: Make sure you have Git installed
3. **Hugging Face Token**: Get your API token from [settings/tokens](https://huggingface.co/settings/tokens)

## 🐳 Deployment Steps

### Step 1: Create a Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Owner**: Your username
   - **Space name**: `resume-ai-helper` (or your preferred name)
   - **License**: Choose appropriate license (MIT recommended)
   - **SDK**: Select **"Docker"**
   - **Hardware**: Choose **"CPU"** (free tier)
4. Click **"Create Space"**

### Step 2: Clone the Space Repository

```bash
# Replace with your actual space URL
git clone https://huggingface.co/spaces/YOUR_USERNAME/resume-ai-helper
cd resume-ai-helper
```

### Step 3: Copy Your App Files

Copy all your app files to the cloned directory:

```bash
# Copy from your local project
cp -r /path/to/your/ResumeAI-Helper/* .
```

**Required files:**
- `app.py` - Main Streamlit application
- `utils.py` - Utility functions
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `.dockerignore` - Docker ignore rules

### Step 4: Configure Hugging Face Token

For the app to work with Hugging Face models, you need to set up your API token:

1. **Option A: Environment Variable (Recommended)**
   - Go to your Space settings
   - Add environment variable: `HF_TOKEN`
   - Value: Your Hugging Face API token (starts with `hf_`)

2. **Option B: Secrets (Alternative)**
   - In your Space settings, go to "Repository secrets"
   - Add secret: `HF_TOKEN`
   - Value: Your Hugging Face API token

### Step 5: Deploy

```bash
# Add all files
git add .

# Commit changes
git commit -m "Initial deployment of ResumeAI-Helper"

# Push to Hugging Face
git push
```

### Step 6: Monitor Deployment

1. Go to your Space page on Hugging Face
2. Watch the build logs
3. Wait for status to change from "Building" to "Running"

## 🔧 Configuration

### Environment Variables

You can set these in your Space settings:

- `HF_TOKEN`: Your Hugging Face API token
- `STREAMLIT_SERVER_PORT`: 7860 (default)
- `STREAMLIT_SERVER_ADDRESS`: 0.0.0.0 (default)

### Hardware Options

- **CPU (Free)**: 16GB RAM, 2 vCPU - Good for basic usage
- **GPU (Paid)**: For faster inference with larger models

## 🌐 Accessing Your App

Once deployed, your app will be available at:
```
https://YOUR_USERNAME-resume-ai-helper.hf.space
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check the build logs in your Space
   - Ensure all dependencies are in `requirements.txt`
   - Verify Dockerfile syntax

2. **App Won't Start**
   - Check if port 7860 is exposed
   - Verify Streamlit command in Dockerfile
   - Check environment variables

3. **Hugging Face API Errors**
   - Verify your API token is correct
   - Check token permissions (needs 'read' access)
   - Try different models if one fails

4. **Memory Issues**
   - Upgrade to paid tier for more RAM
   - Use smaller models
   - Optimize your app code

### Getting Help

- **Hugging Face Documentation**: [docs.huggingface.co](https://docs.huggingface.co)
- **Spaces Documentation**: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- **Community Forum**: [discuss.huggingface.co](https://discuss.huggingface.co)

## 🎯 Next Steps

After successful deployment:

1. **Test your app** thoroughly
2. **Share the URL** with others
3. **Monitor usage** and performance
4. **Update regularly** with new features

## 📝 Notes

- **Free tier limits**: 16GB RAM, 2 vCPU, no GPU
- **Auto-sleep**: Free spaces sleep after inactivity
- **Custom domains**: Available with paid plans
- **Collaboration**: You can add collaborators to your Space

---

**Happy Deploying! 🚀** 