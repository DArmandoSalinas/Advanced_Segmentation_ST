# 🚀 Google Cloud Platform (GCP) Deployment Guide

Complete guide for deploying Streamlit applications to Google Cloud Platform with comprehensive IAM configuration.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [IAM Configuration](#iam-configuration)
4. [Deployment Options](#deployment-options)
5. [Security Configuration](#security-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### 1. Google Cloud Account
- **Google Cloud Account**: Sign up at https://cloud.google.com
- **Billing Account**: Required for most services (free tier available)
- **Payment Method**: Credit card or other payment method

### 2. Local Tools
- **Google Cloud SDK (gcloud CLI)**: [Installation Guide](https://cloud.google.com/sdk/docs/install)
- **Docker** (for Cloud Run deployments): [Installation Guide](https://docs.docker.com/get-docker/)
- **Git** (for version control)

### 3. Verify Installation
```bash
# Check gcloud version
gcloud --version

# Check Docker
docker --version

# Authenticate with Google Cloud
gcloud auth login
```

---

## Initial Setup

### Step 1: Create GCP Project

```bash
# Set project variables (customize for your app)
export PROJECT_ID="your-app-name"
export PROJECT_NAME="Your App Name"
export REGION="us-central1"  # or your preferred region

# Create new project
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"

# Set as active project
gcloud config set project $PROJECT_ID

# Link billing account (replace BILLING_ACCOUNT_ID with your billing account ID)
gcloud beta billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

**Via Console:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name and ID
4. Click "Create"
5. Go to "Billing" → Link billing account

### Step 2: Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API (for container builds)
gcloud services enable cloudbuild.googleapis.com

# Enable Artifact Registry API (for storing Docker images)
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Logging API
gcloud services enable logging.googleapis.com

# Enable Cloud Monitoring API
gcloud services enable monitoring.googleapis.com

# Enable Secret Manager API (for sensitive data)
gcloud services enable secretmanager.googleapis.com

# Enable Compute Engine API (if using VMs)
gcloud services enable compute.googleapis.com

# Enable App Engine API (if using App Engine)
gcloud services enable appengine.googleapis.com

# Verify enabled APIs
gcloud services list --enabled
```

**Via Console:**
1. Go to "APIs & Services" → "Library"
2. Search and enable each API listed above

### Step 3: Configure Project Settings

```bash
# Set default region and zone
gcloud config set compute/region $REGION
gcloud config set compute/zone ${REGION}-a

# Enable required APIs for your region
gcloud compute project-info add-metadata --metadata=google-compute-default-region=$REGION
```

---

## IAM Configuration

### Understanding IAM Basics

**IAM Components:**
- **Principals**: Users, service accounts, groups
- **Roles**: Collections of permissions
- **Permissions**: Specific actions allowed
- **Policies**: Bindings between principals and roles

### Step 1: Create Service Accounts

Service accounts are recommended for application deployments (better security than user accounts).

```bash
# Create service account for Cloud Run deployment
gcloud iam service-accounts create cloud-run-sa \
    --display-name="Cloud Run Service Account" \
    --description="Service account for Cloud Run deployments"

# Create service account for Cloud Build
gcloud iam service-accounts create cloud-build-sa \
    --display-name="Cloud Build Service Account" \
    --description="Service account for Cloud Build operations"

# Create service account for application runtime (if needed)
gcloud iam service-accounts create app-runtime-sa \
    --display-name="Application Runtime Service Account" \
    --description="Service account for application runtime operations"
```

**Via Console:**
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter name and description
4. Click "Create and Continue"

### Step 2: Assign IAM Roles to Service Accounts

#### For Cloud Run Service Account:

```bash
# Get service account email
export CLOUD_RUN_SA="${PROJECT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant Cloud Run Admin role (for deployment)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Grant Service Account User role (to run as service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Grant Storage Admin (if accessing Cloud Storage)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

#### For Cloud Build Service Account:

```bash
# Grant Cloud Build Service Account role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

# Grant Service Account User (to deploy using service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Grant Cloud Run Admin (to deploy to Cloud Run)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Grant Storage Admin (to access build artifacts)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Grant Artifact Registry Writer (to push Docker images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cloud-build-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"
```

#### For Application Runtime Service Account:

```bash
# Grant minimal permissions for runtime (principle of least privilege)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# If accessing Cloud Storage (read-only example)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# If accessing Secret Manager
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

**Via Console:**
1. Go to "IAM & Admin" → "IAM"
2. Find your service account
3. Click "Edit" (pencil icon)
4. Click "Add Another Role"
5. Select role and save

### Step 3: Configure User IAM Permissions

#### For Developers (minimum permissions for deployment):

```bash
# Replace USER_EMAIL with actual developer email
export USER_EMAIL="developer@example.com"

# Grant Cloud Run Admin (to deploy)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="roles/run.admin"

# Grant Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# Grant Cloud Build Editor
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="roles/cloudbuild.builds.editor"

# Grant Storage Admin (if needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="roles/storage.admin"
```

#### For Viewers (read-only access):

```bash
# Grant Viewer role (read-only access to all resources)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="roles/viewer"
```

#### For Admins (full access):

```bash
# Grant Owner role (full access - use with caution)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="roles/owner"
```

### Step 4: Create IAM Custom Roles (Optional)

For fine-grained permissions, create custom roles:

```bash
# Create custom role definition file
cat > custom-role-definition.yaml <<EOF
title: "Streamlit App Deployer"
description: "Custom role for deploying Streamlit applications"
stage: "GA"
includedPermissions:
- run.services.create
- run.services.update
- run.services.delete
- run.services.get
- run.services.list
- run.configurations.get
- run.configurations.list
- run.revisions.get
- run.revisions.list
- iam.serviceAccounts.actAs
- cloudbuild.builds.create
- cloudbuild.builds.get
- cloudbuild.builds.list
- storage.objects.create
- storage.objects.get
- storage.objects.list
EOF

# Create the custom role
gcloud iam roles create streamlitDeployer \
    --project=$PROJECT_ID \
    --file=custom-role-definition.yaml

# Assign custom role to user
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:${USER_EMAIL}" \
    --role="projects/${PROJECT_ID}/roles/streamlitDeployer"
```

### Step 5: Verify IAM Configuration

```bash
# List all IAM policy bindings
gcloud projects get-iam-policy $PROJECT_ID

# List service accounts
gcloud iam service-accounts list

# Get policy for specific service account
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com"
```

### Step 6: Create and Download Service Account Keys (if needed)

**⚠️ Security Warning**: Only create keys if absolutely necessary. Prefer using Workload Identity when possible.

```bash
# Create key for service account (only if needed)
gcloud iam service-accounts keys create ~/cloud-run-sa-key.json \
    --iam-account=cloud-run-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Set environment variable for authentication
export GOOGLE_APPLICATION_CREDENTIALS=~/cloud-run-sa-key.json
```

**Best Practice**: Use Workload Identity instead of service account keys for better security.

---

## Deployment Options

### Option 1: Cloud Run (Recommended) ⭐

**Best for:** Serverless deployments, automatic scaling, pay-per-use

#### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT environment variable)
ENV PORT=8080
EXPOSE 8080

# Run Streamlit app
CMD streamlit run app/streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
```

#### Create .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.git
.gitignore
README.md
.env
.venv
*.md
docs/
notebooks/
*.ipynb
```

#### Create cloudbuild.yaml (for CI/CD)

```yaml
# cloudbuild.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/streamlit-app:$SHORT_SHA', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/streamlit-app:$SHORT_SHA']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'streamlit-app'
      - '--image=gcr.io/$PROJECT_ID/streamlit-app:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--service-account=app-runtime-sa@$PROJECT_ID.iam.gserviceaccount.com'
      - '--memory=2Gi'
      - '--cpu=2'
      - '--max-instances=10'
      - '--min-instances=0'
      - '--timeout=300'

images:
  - 'gcr.io/$PROJECT_ID/streamlit-app:$SHORT_SHA'
```

#### Deploy to Cloud Run

**Option A: Direct Deployment (Quick Start)**

```bash
# Deploy directly from source
gcloud run deploy streamlit-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account=app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0 \
    --timeout=300 \
    --set-env-vars="PYARROW_IGNORE_TIMEZONE=1"
```

**Option B: Build and Deploy (Recommended for Production)**

```bash
# Build container image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/streamlit-app

# Deploy to Cloud Run
gcloud run deploy streamlit-app \
    --image gcr.io/${PROJECT_ID}/streamlit-app \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account=app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0 \
    --timeout=300 \
    --set-env-vars="PYARROW_IGNORE_TIMEZONE=1"
```

**Option C: Using Cloud Build (CI/CD)**

```bash
# Submit build using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml
```

#### Get Service URL

```bash
# Get service URL
gcloud run services describe streamlit-app \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)'
```

#### Update Deployment

```bash
# Update with new code
gcloud run deploy streamlit-app \
    --source . \
    --platform managed \
    --region us-central1
```

### Option 2: App Engine

**Best for:** Traditional PaaS deployments, automatic scaling

#### Create app.yaml

```yaml
# app.yaml
runtime: python39

entrypoint: streamlit run app/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0

env_variables:
  PYARROW_IGNORE_TIMEZONE: '1'

automatic_scaling:
  min_instances: 1
  max_instances: 3
  target_cpu_utilization: 0.6

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10
```

#### Deploy to App Engine

```bash
# Initialize App Engine (first time only)
gcloud app create --region=$REGION

# Deploy application
gcloud app deploy

# Open in browser
gcloud app browse
```

### Option 3: Compute Engine (VM)

**Best for:** Full control, predictable costs, custom configurations

#### Create VM Instance

```bash
# Create VM instance
gcloud compute instances create streamlit-app-vm \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server \
    --service-account=app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform

# Get external IP
gcloud compute instances describe streamlit-app-vm \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

#### SSH into VM and Setup

```bash
# SSH into VM
gcloud compute ssh streamlit-app-vm

# Inside VM, install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv git

# Clone your repository
git clone YOUR_REPO_URL
cd YOUR_REPO_NAME

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

#### Configure Firewall Rules

```bash
# Allow HTTP traffic
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server

# Allow HTTPS traffic
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server

# Allow Streamlit port (if not using reverse proxy)
gcloud compute firewall-rules create allow-streamlit \
    --allow tcp:8501 \
    --source-ranges 0.0.0.0/0 \
    --target-tags streamlit-server
```

---

## Security Configuration

### 1. Enable Authentication for Cloud Run

```bash
# Remove public access (require authentication)
gcloud run services update streamlit-app \
    --platform managed \
    --region us-central1 \
    --no-allow-unauthenticated

# Grant invoker role to specific users/groups
gcloud run services add-iam-policy-binding streamlit-app \
    --platform managed \
    --region us-central1 \
    --member="user:user@example.com" \
    --role="roles/run.invoker"

# Or grant to all authenticated users
gcloud run services add-iam-policy-binding streamlit-app \
    --platform managed \
    --region us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

### 2. Use Secret Manager for Sensitive Data

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create my-secret \
    --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding my-secret \
    --member="serviceAccount:app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Access secret in Cloud Run
gcloud run services update streamlit-app \
    --platform managed \
    --region us-central1 \
    --update-secrets=SECRET_NAME=my-secret:latest
```

### 3. Configure VPC and Network Security

```bash
# Create VPC network (if needed)
gcloud compute networks create app-network \
    --subnet-mode=auto

# Create firewall rule for internal traffic only
gcloud compute firewall-rules create allow-internal \
    --network app-network \
    --allow tcp,udp,icmp \
    --source-ranges 10.0.0.0/8
```

### 4. Enable Cloud Armor (DDoS Protection)

```bash
# Create Cloud Armor security policy
gcloud compute security-policies create app-security-policy \
    --description "Security policy for Streamlit app"

# Add rule to allow specific IPs
gcloud compute security-policies rules create 1000 \
    --security-policy app-security-policy \
    --expression "origin.ip == 'YOUR_IP_ADDRESS'" \
    --action allow
```

---

## Monitoring & Maintenance

### 1. Set Up Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create streamlit-uptime \
    --display-name="Streamlit App Uptime Check" \
    --http-check-path="/" \
    --http-check-host="YOUR_CLOUD_RUN_URL"

# Create alerting policy (example)
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05 \
    --condition-threshold-duration=300s
```

### 2. View Logs

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-app" \
    --limit 50 \
    --format json

# Stream logs in real-time
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-app"
```

### 3. Set Budget Alerts

```bash
# Create budget alert
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Streamlit App Budget" \
    --budget-amount=100USD \
    --threshold-rule=percent=80 \
    --threshold-rule=percent=100 \
    --notification-rule=pubsub-topic=projects/${PROJECT_ID}/topics/budget-alerts
```

---

## Troubleshooting

### Common Issues

#### 1. Permission Denied Errors

```bash
# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:app-runtime-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account has required roles
gcloud projects get-iam-policy $PROJECT_ID \
    --format="table(bindings.role,bindings.members)"
```

#### 2. Build Failures

```bash
# Check build logs
gcloud builds list --limit=5

# View specific build logs
gcloud builds log BUILD_ID
```

#### 3. Deployment Failures

```bash
# Check Cloud Run service status
gcloud run services describe streamlit-app \
    --platform managed \
    --region us-central1

# View recent revisions
gcloud run revisions list \
    --service streamlit-app \
    --platform managed \
    --region us-central1
```

#### 4. Application Not Starting

```bash
# Check application logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-app AND severity>=ERROR" \
    --limit 20

# Verify environment variables
gcloud run services describe streamlit-app \
    --platform managed \
    --region us-central1 \
    --format="value(spec.template.spec.containers[0].env)"
```

---

## Cost Optimization

### 1. Cloud Run Cost Optimization

```bash
# Set minimum instances to 0 (no cost when idle)
gcloud run services update streamlit-app \
    --platform managed \
    --region us-central1 \
    --min-instances=0 \
    --max-instances=5

# Adjust memory allocation
gcloud run services update streamlit-app \
    --platform managed \
    --region us-central1 \
    --memory=1Gi \
    --cpu=1
```

### 2. Enable Cloud Run Free Tier

- **First 2 million requests/month**: Free
- **First 400,000 GB-seconds**: Free
- **First 200,000 vCPU-seconds**: Free

### 3. Set Resource Limits

```bash
# Create quota limits
gcloud compute project-info describe \
    --format="value(quotas.metric,quotas.limit,quotas.usage)"
```

---

## Quick Reference Commands

### IAM Commands

```bash
# List all IAM bindings
gcloud projects get-iam-policy PROJECT_ID

# Add IAM binding
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="MEMBER" \
    --role="ROLE"

# Remove IAM binding
gcloud projects remove-iam-policy-binding PROJECT_ID \
    --member="MEMBER" \
    --role="ROLE"

# List service accounts
gcloud iam service-accounts list

# Create service account
gcloud iam service-accounts create NAME \
    --display-name="DISPLAY_NAME"

# Grant role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:EMAIL" \
    --role="ROLE"
```

### Deployment Commands

```bash
# Deploy to Cloud Run
gcloud run deploy SERVICE_NAME \
    --source . \
    --region REGION \
    --platform managed

# Update service
gcloud run services update SERVICE_NAME \
    --region REGION

# View service details
gcloud run services describe SERVICE_NAME \
    --region REGION

# List services
gcloud run services list --region REGION

# Delete service
gcloud run services delete SERVICE_NAME \
    --region REGION
```

### Logging Commands

```bash
# View logs
gcloud logging read "QUERY" --limit 50

# Stream logs
gcloud logging tail "QUERY"

# Export logs
gcloud logging export logs.txt "QUERY"
```

---

## Additional Resources

- [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Service Accounts Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)

---

## Checklist for Deployment

### Pre-Deployment
- [ ] Create GCP project
- [ ] Link billing account
- [ ] Enable required APIs
- [ ] Create service accounts
- [ ] Configure IAM roles and permissions
- [ ] Set up authentication (if needed)
- [ ] Prepare Dockerfile/app.yaml
- [ ] Test locally

### Deployment
- [ ] Build container image
- [ ] Deploy to Cloud Run/App Engine/VM
- [ ] Verify deployment
- [ ] Test application functionality
- [ ] Configure custom domain (if needed)
- [ ] Set up SSL/HTTPS

### Post-Deployment
- [ ] Configure monitoring and alerts
- [ ] Set up logging
- [ ] Create budget alerts
- [ ] Document access and URLs
- [ ] Set up CI/CD (optional)
- [ ] Configure backup strategy (if needed)

---

## Support

For issues or questions:
1. Check [Google Cloud Status](https://status.cloud.google.com)
2. Review [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
3. Consult [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-run)
4. Contact Google Cloud Support

---

**Last Updated**: 2024
**Version**: 1.0

