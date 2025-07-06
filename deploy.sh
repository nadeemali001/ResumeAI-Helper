#!/bin/bash

# 🚀 ResumeAI-Helper Deployment Script
# This script helps deploy your app to Hugging Face Spaces

echo "🚀 ResumeAI-Helper Deployment Script"
echo "======================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "Dockerfile" ]; then
    echo "❌ Please run this script from the ResumeAI-Helper directory"
    exit 1
fi

echo "✅ Found app.py and Dockerfile"

# Ask for Hugging Face username
read -p "Enter your Hugging Face username: " HF_USERNAME

# Ask for space name
read -p "Enter your space name (default: resume-ai-helper): " SPACE_NAME
SPACE_NAME=${SPACE_NAME:-resume-ai-helper}

# Create space URL
SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

echo ""
echo "📋 Deployment Summary:"
echo "Username: $HF_USERNAME"
echo "Space Name: $SPACE_NAME"
echo "Space URL: $SPACE_URL"
echo ""

# Confirm deployment
read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🔧 Setting up deployment..."

# Create deployment directory
DEPLOY_DIR="../resume-ai-helper-deploy"
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
git remote add origin "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

# Push to Hugging Face
echo "🚀 Pushing to Hugging Face..."
git push -u origin main

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to: $SPACE_URL"
echo "2. Wait for the build to complete (may take 5-10 minutes)"
echo "3. Add your HF_TOKEN in the Space settings"
echo "4. Test your app!"
echo ""
echo "🔧 To update your app later:"
echo "cd $DEPLOY_DIR"
echo "git add . && git commit -m 'Update' && git push"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md" 