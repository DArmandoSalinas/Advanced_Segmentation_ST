#!/bin/bash
# Script para crear y configurar el bucket compartido del proyecto
# Project: advseg-477918
# Bucket: data_clusters

set -e

PROJECT_ID="advseg-477918"
BUCKET_NAME="data_clusters"
REGION="us-central1"
SERVICE_NAME="streamlit-app"

echo "📦 Creando y configurando bucket compartido del proyecto"
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

# Get the Cloud Run service account
echo ""
echo "🔍 Obteniendo cuenta de servicio de Cloud Run..."
SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(spec.template.spec.serviceAccountName)' \
    --project $PROJECT_ID 2>/dev/null || echo "")

if [ -z "$SERVICE_ACCOUNT" ]; then
    # Use default compute service account
    SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
    echo "⚠️ Usando cuenta de servicio por defecto: $SERVICE_ACCOUNT"
else
    echo "✅ Cuenta de servicio encontrada: $SERVICE_ACCOUNT"
fi

# Also try the compute service account (common default)
COMPUTE_SA="${PROJECT_ID}@compute.gserviceaccount.com"

# Grant Storage Object Viewer role (for reading)
echo ""
echo "🔐 Otorgando permisos de lectura (Storage Object Viewer)..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectViewer" \
    --quiet || echo "⚠️ No se pudo otorgar a $SERVICE_ACCOUNT"

if [ "$SERVICE_ACCOUNT" != "$COMPUTE_SA" ]; then
    gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
        --member="serviceAccount:$COMPUTE_SA" \
        --role="roles/storage.objectViewer" \
        --quiet || echo "⚠️ No se pudo otorgar a $COMPUTE_SA"
fi

# Grant Storage Object Creator role (for writing/uploads)
echo "🔐 Otorgando permisos de escritura (Storage Object Creator)..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectCreator" \
    --quiet || echo "⚠️ No se pudo otorgar escritura a $SERVICE_ACCOUNT"

if [ "$SERVICE_ACCOUNT" != "$COMPUTE_SA" ]; then
    gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
        --member="serviceAccount:$COMPUTE_SA" \
        --role="roles/storage.objectCreator" \
        --quiet || echo "⚠️ No se pudo otorgar escritura a $COMPUTE_SA"
fi

echo ""
echo "✅ Bucket configurado exitosamente!"
echo ""
echo "📋 Información del bucket:"
echo "   Nombre: $BUCKET_NAME"
echo "   URL: https://console.cloud.google.com/storage/browser/$BUCKET_NAME"
echo ""
echo "📝 Los usuarios pueden subir archivos de 3 formas:"
echo ""
echo "1. 🌐 Desde la Consola de GCP (Más fácil):"
echo "   https://console.cloud.google.com/storage/browser/$BUCKET_NAME"
echo "   → Click en 'Upload' → Selecciona archivo → Listo"
echo ""
echo "2. 💻 Desde la línea de comandos (gsutil):"
echo "   gsutil cp archivo.csv gs://$BUCKET_NAME/"
echo ""
echo "3. 📤 Desde la aplicación (Automático):"
echo "   → Selecciona '⬆️ Subir CSV' → Si es grande, se sube automáticamente"
echo ""
echo "✅ ¡Todo listo! Los usuarios ya pueden subir archivos al bucket."

