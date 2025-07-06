#!/bin/bash

# 🚀 Quick Deployment Script for ResumeAI-Helper
# Usage: ./quick_deploy.sh YOUR_USERNAME SPACE_NAME

echo "🚀 ResumeAI-Helper Quick Deployment"
echo "===================================="

# Check arguments
if [ $# -ne 2 ]; then
    echo "❌ Usage: ./quick_deploy.sh <username> <space_name>"
    echo "Example: ./quick_deploy.sh john resume-ai-helper"
    exit 1
fi

USERNAME=$1
SPACE_NAME=$2
SPACE_URL="https://huggingface.co/spaces/$USERNAME/$SPACE_NAME"

echo "📋 Deployment Details:"
echo "Username: $USERNAME"
echo "Space Name: $SPACE_NAME"
echo "Space URL: $SPACE_URL"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "Dockerfile" ]; then
    echo "❌ Please run this script from the ResumeAI-Helper directory"
    exit 1
fi

echo "✅ Found app.py and Dockerfile"

# Create deployment directory
DEPLOY_DIR="../resume-ai-helper-deploy"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy necessary files
echo "📁 Copying files..."
cp app.py "$DEPLOY_DIR/"
cp utils.py "$DEPLOY_DIR/"
cp requirements.txt "$DEPLOY_DIR/"
cp Dockerfile "$DEPLOY_DIR/"
cp .dockerignore "$DEPLOY_DIR/"

# Change to deployment directory
cd "$DEPLOY_DIR"

# Initialize git repository
echo "🔧 Initializing git repository..."
git init

# Add files
echo "📝 Adding files to git..."
git add .

# Initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial deployment of ResumeAI-Helper"

# Add remote
echo "🔗 Adding Hugging Face remote..."
git remote set-url origin https://<user_name>:<token>@huggingface.co/spaces/Nadeemali001/ResumeAI.git

# Push to Hugging Face
echo "🚀 Pushing to Hugging Face..."
echo "You may be prompted for your Hugging Face credentials..."
git push origin main

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to: $SPACE_URL"
echo "2. Wait for the build to complete (may take 5-10 minutes)"
echo "3. Add your HF_TOKEN in the Space settings:"
echo "   - Go to Settings > Repository secrets"
echo "   - Add secret: HF_TOKEN"
echo "   - Value: Your Hugging Face API token (starts with hf_)"
echo "4. Test your app!"
echo ""
echo "🔧 To update your app later:"
echo "cd $DEPLOY_DIR"
echo "git add . && git commit -m 'Update' && git push"

huggingface-cli login 