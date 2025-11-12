#!/bin/bash
# Script para configurar Cloud Storage para archivos grandes
# Project: advseg-477918

set -e

PROJECT_ID="advseg-477918"
BUCKET_NAME="${1:-advseg-data-bucket}"
REGION="us-central1"

echo "☁️ Configurando Cloud Storage para archivos grandes"
echo "Project: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Enable Storage API
echo "🔧 Habilitando Storage API..."
gcloud services enable storage.googleapis.com --quiet

# Create bucket if it doesn't exist
echo "📦 Creando bucket (si no existe)..."
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "✅ Bucket $BUCKET_NAME ya existe"
else
    echo "📦 Creando bucket $BUCKET_NAME..."
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "✅ Bucket creado exitosamente"
fi

# Get the default Cloud Run service account
SERVICE_ACCOUNT=$(gcloud run services describe streamlit-app \
    --platform managed \
    --region $REGION \
    --format 'value(spec.template.spec.serviceAccountName)' \
    --project $PROJECT_ID 2>/dev/null || echo "")

if [ -z "$SERVICE_ACCOUNT" ]; then
    # Use default compute service account
    SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
    echo "⚠️ Usando cuenta de servicio por defecto: $SERVICE_ACCOUNT"
else
    echo "✅ Usando cuenta de servicio: $SERVICE_ACCOUNT"
fi

# Grant Storage Object Viewer and Creator roles to the service account
echo "🔐 Otorgando permisos de lectura y escritura al servicio..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectViewer" \
    --quiet

gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectCreator" \
    --quiet

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Sube tu archivo CSV al bucket:"
echo "   gsutil cp contacts_campus_Qro_.csv gs://$BUCKET_NAME/datos/"
echo ""
echo "2. O usa la consola de GCP:"
echo "   https://console.cloud.google.com/storage/browser/$BUCKET_NAME"
echo ""
echo "3. En la aplicación, selecciona '☁️ Cargar desde Cloud Storage'"
echo "   - Bucket: $BUCKET_NAME"
echo "   - Ruta: datos/contacts_campus_Qro_.csv (o la ruta que uses)"
echo ""

