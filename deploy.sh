#!/bin/bash

# 🚀 ResumeAI-Helper Deployment Script
# This script helps deploy your app to various cloud platforms

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

# Ask for deployment platform
echo ""
echo "🌐 Choose your deployment platform:"
echo "1. Streamlit Cloud (Recommended)"
echo "2. Hugging Face Spaces"
echo "3. Google Cloud Run"
echo "4. Heroku"
echo "5. Local Docker"
read -p "Enter your choice (1-5): " PLATFORM_CHOICE

case $PLATFORM_CHOICE in
    1)
        echo "🚀 Deploying to Streamlit Cloud..."
        deploy_streamlit_cloud
        ;;
    2)
        echo "🚀 Deploying to Hugging Face Spaces..."
        deploy_huggingface
        ;;
    3)
        echo "🚀 Deploying to Google Cloud Run..."
        deploy_google_cloud
        ;;
    4)
        echo "🚀 Deploying to Heroku..."
        deploy_heroku
        ;;
    5)
        echo "🐳 Running with Docker locally..."
        deploy_docker_local
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

# Function to deploy to Streamlit Cloud
deploy_streamlit_cloud() {
    echo ""
    echo "📋 Streamlit Cloud Deployment"
    echo "=============================="
    
    # Check if git remote exists
    if ! git remote get-url origin &> /dev/null; then
        echo "❌ No git remote found. Please add your GitHub repository as origin:"
        echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
        exit 1
    fi
    
    echo "✅ Found git remote: $(git remote get-url origin)"
    
    # Push to GitHub
    echo "📤 Pushing to GitHub..."
    git add .
    git commit -m "Update for Google Gemini integration"
    git push origin main
    
    echo ""
    echo "🎉 Code pushed to GitHub!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to: https://share.streamlit.io"
    echo "2. Connect your GitHub repository"
    echo "3. Set the path to: app.py"
    echo "4. Add your GEMINI_API_KEY in the secrets section"
    echo "5. Deploy!"
    echo ""
    echo "🔑 To get your Google Gemini API key:"
    echo "Visit: https://makersuite.google.com/app/apikey"
}

# Function to deploy to Hugging Face Spaces
deploy_huggingface() {
    echo ""
    echo "📋 Hugging Face Spaces Deployment"
    echo "================================="
    
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
    git commit -m "Initial deployment of ResumeAI-Helper with Google Gemini"
    
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
    echo "3. Add your GEMINI_API_KEY in the Space settings"
    echo "4. Test your app!"
    echo ""
    echo "🔧 To update your app later:"
    echo "cd $DEPLOY_DIR"
    echo "git add . && git commit -m 'Update' && git push"
}

# Function to deploy to Google Cloud Run
deploy_google_cloud() {
    echo ""
    echo "📋 Google Cloud Run Deployment"
    echo "=============================="
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo "❌ Google Cloud CLI is not installed."
        echo "Please install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo "❌ Not authenticated with Google Cloud."
        echo "Please run: gcloud auth login"
        exit 1
    fi
    
    # Ask for project ID
    read -p "Enter your Google Cloud project ID: " PROJECT_ID
    
    # Ask for region
    read -p "Enter region (default: us-central1): " REGION
    REGION=${REGION:-us-central1}
    
    # Ask for API key
    read -p "Enter your Google Gemini API key: " GEMINI_API_KEY
    
    echo ""
    echo "📋 Deployment Summary:"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo ""
    
    # Confirm deployment
    read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
    
    echo ""
    echo "🚀 Deploying to Google Cloud Run..."
    
    # Set project
    gcloud config set project "$PROJECT_ID"
    
    # Enable required APIs
    gcloud services enable run.googleapis.com
    
    # Deploy
    gcloud run deploy resumeai-helper \
        --source . \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY"
    
    echo ""
    echo "🎉 Deployment completed!"
    echo ""
    echo "📋 Your app is now running on Google Cloud Run!"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo ""
    echo "📋 Heroku Deployment"
    echo "===================="
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI is not installed."
        echo "Please install it from: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Check if user is logged in
    if ! heroku auth:whoami &> /dev/null; then
        echo "❌ Not logged in to Heroku."
        echo "Please run: heroku login"
        exit 1
    fi
    
    # Ask for app name
    read -p "Enter your Heroku app name: " APP_NAME
    
    # Ask for API key
    read -p "Enter your Google Gemini API key: " GEMINI_API_KEY
    
    echo ""
    echo "📋 Deployment Summary:"
    echo "App Name: $APP_NAME"
    echo ""
    
    # Confirm deployment
    read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
    
    echo ""
    echo "🚀 Deploying to Heroku..."
    
    # Create Heroku app
    heroku create "$APP_NAME"
    
    # Set environment variables
    heroku config:set GEMINI_API_KEY="$GEMINI_API_KEY"
    
    # Deploy
    git push heroku main
    
    echo ""
    echo "🎉 Deployment completed!"
    echo ""
    echo "📋 Your app is now running on Heroku!"
    echo "URL: https://$APP_NAME.herokuapp.com"
}

# Function to run with Docker locally
deploy_docker_local() {
    echo ""
    echo "📋 Local Docker Deployment"
    echo "=========================="
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed."
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Ask for API key
    read -p "Enter your Google Gemini API key: " GEMINI_API_KEY
    
    echo ""
    echo "📋 Local Deployment Summary:"
    echo "Port: 8501"
    echo "URL: http://localhost:8501"
    echo ""
    
    # Confirm deployment
    read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
    
    echo ""
    echo "🐳 Building Docker image..."
    docker build -t resumeai-helper .
    
    echo ""
    echo "🚀 Starting container..."
    docker run -p 8501:8501 -e GEMINI_API_KEY="$GEMINI_API_KEY" resumeai-helper
    
    echo ""
    echo "🎉 Container started!"
    echo ""
    echo "📋 Your app is now running locally!"
    echo "URL: http://localhost:8501"
    echo ""
    echo "💡 To stop the container, press Ctrl+C"
}

echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md" 