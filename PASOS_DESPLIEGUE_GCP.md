# 🚀 Guía de Despliegue a Google Cloud Platform

## 📋 Resumen

Esta guía te ayudará a desplegar tu aplicación Streamlit en Google Cloud Run. El proyecto ya está configurado con:
- ✅ Dockerfile listo
- ✅ Script de despliegue (`deploy.sh`)
- ✅ Configuración de Cloud Build (`cloudbuild.yaml`)
- ✅ `.dockerignore` configurado

## 🎯 Pasos a Seguir

### Paso 1: Verificar Instalación de Herramientas

Asegúrate de tener instalado:

```bash
# Verificar Google Cloud SDK
gcloud --version

# Verificar Docker
docker --version
```

**Si no los tienes instalados:**
- Google Cloud SDK: https://cloud.google.com/sdk/docs/install
- Docker: https://docs.docker.com/get-docker/

### Paso 2: Autenticarse en Google Cloud

```bash
# Iniciar sesión en Google Cloud
gcloud auth login

# Configurar el proyecto (ya está configurado como advseg-477918)
gcloud config set project advseg-477918

# Verificar que estás en el proyecto correcto
gcloud config get-value project
```

### Paso 3: Habilitar APIs Necesarias

Ejecuta estos comandos para habilitar los servicios requeridos:

```bash
# Habilitar Cloud Run API
gcloud services enable run.googleapis.com

# Habilitar Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Habilitar Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Habilitar Storage API (para Cloud Storage)
gcloud services enable storage.googleapis.com

# Verificar APIs habilitadas
gcloud services list --enabled
```

### Paso 3.5: Crear y Configurar el Bucket Compartido

**⚠️ IMPORTANTE:** El bucket `data_clusters` es donde los usuarios subirán sus archivos CSV. Debes crearlo antes del despliegue.

**Opción A: Usar el script automático (Recomendado)**

```bash
./crear_bucket_proyecto.sh
```

Este script:
- ✅ Crea el bucket `data_clusters` si no existe
- ✅ Otorga permisos al servicio de Cloud Run
- ✅ Configura todo automáticamente

**Opción B: Manualmente**

```bash
# Crear bucket
gsutil mb -l us-central1 gs://data_clusters

# Otorgar permisos (ver crear_bucket_proyecto.sh para el comando completo)
./otorgar_permisos_bucket.sh data_clusters
```

**Verificar que el bucket existe:**
```bash
gsutil ls -b gs://data_clusters
```

### Paso 4: Verificar Billing

Asegúrate de que tu proyecto tenga una cuenta de facturación vinculada:

1. Ve a la consola de GCP: https://console.cloud.google.com
2. Selecciona el proyecto `advseg-477918`
3. Ve a "Billing" en el menú
4. Si no hay cuenta vinculada, vincula una cuenta de facturación

**Nota:** Cloud Run tiene un tier gratuito generoso (2 millones de requests/mes gratis)

### Paso 5: Desplegar la Aplicación

Tienes dos opciones:

#### Opción A: Usar el Script Automático (Recomendado)

```bash
# Dar permisos de ejecución al script
chmod +x deploy.sh

# Ejecutar el despliegue
./deploy.sh
```

Este script:
- Configura el proyecto
- Habilita las APIs necesarias
- Construye y despliega la aplicación
- Te muestra la URL de tu aplicación

#### Opción B: Despliegue Manual

```bash
# Configurar proyecto
gcloud config set project advseg-477918

# Desplegar directamente desde el código fuente
gcloud run deploy streamlit-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0 \
    --timeout=300 \
    --set-env-vars="PYARROW_IGNORE_TIMEZONE=1"
```

### Paso 6: Obtener la URL de tu Aplicación

Después del despliegue, obtén la URL:

```bash
gcloud run services describe streamlit-app \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)'
```

O simplemente revisa la salida del script `deploy.sh` que mostrará la URL automáticamente.

## 🔧 Configuración Actual

- **Project ID:** `advseg-477918`
- **Region:** `us-central1`
- **Service Name:** `streamlit-app`
- **Memory:** 2GB
- **CPU:** 2 cores
- **Max Instances:** 10
- **Min Instances:** 0 (se apaga cuando no hay tráfico)

## 📝 Comandos Útiles

### Ver el estado del servicio
```bash
gcloud run services describe streamlit-app \
    --platform managed \
    --region us-central1
```

### Ver logs en tiempo real
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-app"
```

### Actualizar el despliegue (después de hacer cambios)
```bash
./deploy.sh
# O manualmente:
gcloud run deploy streamlit-app --source . --region us-central1
```

### Eliminar el servicio (si es necesario)
```bash
gcloud run services delete streamlit-app \
    --platform managed \
    --region us-central1
```

## ⚠️ Notas Importantes

1. **Primera vez:** El primer despliegue puede tardar 5-10 minutos mientras se construye la imagen Docker.

2. **Costos:** Con la configuración actual (min-instances=0), solo pagarás cuando haya tráfico. El tier gratuito incluye:
   - 2 millones de requests/mes
   - 400,000 GB-segundos
   - 200,000 vCPU-segundos

3. **Archivos de datos:** Si tu aplicación necesita acceder a archivos CSV u otros datos, asegúrate de que estén incluidos en el Dockerfile o considera usar Cloud Storage.

4. **Variables de entorno:** Si necesitas agregar más variables de entorno, edita el `deploy.sh` y agrega más `--set-env-vars`.

## 🐛 Solución de Problemas

### Error: "Permission denied"
```bash
# Verificar que tienes los permisos necesarios
gcloud projects get-iam-policy advseg-477918
```

### Error: "API not enabled"
```bash
# Habilitar todas las APIs necesarias
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### Error: "Billing not enabled"
- Ve a la consola de GCP y vincula una cuenta de facturación

### La aplicación no inicia
```bash
# Revisar logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=streamlit-app AND severity>=ERROR" --limit 20
```

## ✅ Checklist Pre-Despliegue

- [ ] Google Cloud SDK instalado
- [ ] Docker instalado (si usas build local)
- [ ] Autenticado en GCP (`gcloud auth login`)
- [ ] Proyecto configurado (`gcloud config set project advseg-477918`)
- [ ] APIs habilitadas
- [ ] Cuenta de facturación vinculada
- [ ] Script `deploy.sh` tiene permisos de ejecución

## 🎉 ¡Listo!

Una vez completados estos pasos, tu aplicación estará disponible en la URL que te proporcione el despliegue. Puedes compartir esta URL con tus usuarios.

---

**¿Necesitas ayuda?** Revisa el archivo `GOOGLE_CLOUD_DEPLOYMENT_GUIDE.md` para información más detallada sobre configuración avanzada, IAM, seguridad, etc.

