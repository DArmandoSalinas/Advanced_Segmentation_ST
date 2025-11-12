#!/bin/bash
# Deployment script for Google Cloud Run
# Project: advseg

set -e  # Exit on error

# Project configuration
PROJECT_ID="advseg-477918"
REGION="us-central1"
SERVICE_NAME="streamlit-app"

echo "🚀 Deploying Streamlit App to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Set the project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable storage.googleapis.com --quiet

echo ""
echo "📦 Building and deploying to Cloud Run..."
echo "This may take a few minutes..."
echo ""

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0 \
    --timeout=300 \
    --set-env-vars="PYARROW_IGNORE_TIMEZONE=1,GCS_BUCKET_NAME=data_clusters" \
    --project $PROJECT_ID

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📱 Getting your app URL..."
APP_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)

echo ""
echo "🎉 Your app is live at:"
echo "$APP_URL"
echo ""
echo "You can open it in your browser now!"
