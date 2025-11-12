#!/bin/bash
# Script para otorgar permisos al servicio de Cloud Run en un bucket existente
# Project: advseg-477918

set -e

PROJECT_ID="advseg-477918"
BUCKET_NAME="${1:-data_clusters}"
REGION="us-central1"
SERVICE_NAME="streamlit-app"

echo "🔐 Otorgando permisos al servicio de Cloud Run"
echo "Project: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Get the Cloud Run service account
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
echo "🔍 También verificando: $COMPUTE_SA"

# Grant Storage Object Viewer role (for reading)
echo ""
echo "🔐 Otorgando permisos de lectura (Storage Object Viewer)..."
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectViewer" \
    --quiet || echo "⚠️ No se pudo otorgar a $SERVICE_ACCOUNT, intentando con compute service account..."

# Also grant to compute service account if different
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
echo "✅ Permisos otorgados!"
echo ""
echo "📋 Verificar permisos:"
echo "   gcloud storage buckets get-iam-policy gs://$BUCKET_NAME"
echo ""
echo "🔄 Ahora intenta cargar el archivo nuevamente en la aplicación."

