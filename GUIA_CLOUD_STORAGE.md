# ☁️ Guía: Usar Cloud Storage para Archivos Grandes

## 🎯 Problema Resuelto

Si tu archivo CSV es mayor a 32MB, no puedes subirlo directamente a través de la interfaz web debido al límite de Cloud Run. **La solución es usar Google Cloud Storage.**

## ✅ Solución Implementada

He agregado una nueva opción en la aplicación: **"☁️ Cargar desde Cloud Storage"** que te permite:

1. Subir tu archivo grande a un bucket de Cloud Storage
2. Especificar la ruta del archivo en la aplicación
3. La aplicación carga el archivo directamente desde Cloud Storage (sin límite de tamaño)

## 🚀 Pasos para Usar Cloud Storage

### Paso 1: Configurar el Bucket (Solo una vez)

Ejecuta el script de configuración:

```bash
./configurar_cloud_storage.sh
```

O manualmente:

```bash
# Crear bucket
gsutil mb -l us-central1 gs://advseg-data-bucket

# Dar permisos al servicio de Cloud Run
gcloud storage buckets add-iam-policy-binding gs://advseg-data-bucket \
    --member="serviceAccount:advseg-477918@appspot.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### Paso 2: Subir tu Archivo CSV

**Opción A: Desde la línea de comandos (Recomendado)**

```bash
# Subir archivo
gsutil cp contacts_campus_Qro_.csv gs://advseg-data-bucket/datos/

# Verificar que se subió
gsutil ls gs://advseg-data-bucket/datos/
```

**Opción B: Desde la consola de GCP**

1. Ve a: https://console.cloud.google.com/storage
2. Selecciona o crea el bucket `advseg-data-bucket`
3. Haz clic en "Subir archivo"
4. Selecciona tu archivo CSV
5. Anota la ruta completa (ej: `datos/contacts_campus_Qro_.csv`)

### Paso 3: Usar en la Aplicación

1. Abre tu aplicación Streamlit desplegada
2. En la sidebar, selecciona **"☁️ Cargar desde Cloud Storage"**
3. Ingresa:
   - **Nombre del Bucket:** `advseg-data-bucket`
   - **Ruta del archivo:** `datos/contacts_campus_Qro_.csv` (o la ruta que usaste)
4. Haz clic en **"🔄 Cargar desde Cloud Storage"**
5. ¡Listo! El archivo se cargará sin importar su tamaño

## 📋 Ejemplo Completo

```bash
# 1. Configurar (solo una vez)
./configurar_cloud_storage.sh advseg-data-bucket

# 2. Subir archivo
gsutil cp contacts_campus_Qro_.csv gs://advseg-data-bucket/datos/

# 3. En la app:
#    - Bucket: advseg-data-bucket
#    - Ruta: datos/contacts_campus_Qro_.csv
```

## 🔐 Permisos Necesarios

El servicio de Cloud Run necesita el rol `Storage Object Viewer` en el bucket. El script `configurar_cloud_storage.sh` lo configura automáticamente.

Si necesitas hacerlo manualmente:

```bash
# Obtener la cuenta de servicio de Cloud Run
SERVICE_ACCOUNT=$(gcloud run services describe streamlit-app \
    --platform managed \
    --region us-central1 \
    --format 'value(spec.template.spec.serviceAccountName)' \
    --project advseg-477918)

# Otorgar permisos
gcloud storage buckets add-iam-policy-binding gs://advseg-data-bucket \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.objectViewer"
```

## 💡 Ventajas de esta Solución

✅ **Sin límite de tamaño** - Puedes subir archivos de cualquier tamaño  
✅ **Rápido** - Cloud Storage es muy rápido para leer archivos  
✅ **Seguro** - Los archivos están en tu proyecto de GCP  
✅ **Persistente** - El archivo queda guardado para futuros usos  
✅ **Fácil de usar** - Solo necesitas especificar bucket y ruta  

## 🛠️ Troubleshooting

### Error: "Permission denied"

```bash
# Verificar permisos
gcloud storage buckets get-iam-policy gs://advseg-data-bucket

# Otorgar permisos nuevamente
./configurar_cloud_storage.sh
```

### Error: "Bucket not found"

```bash
# Crear el bucket
gsutil mb -l us-central1 gs://advseg-data-bucket
```

### Error: "File not found"

Verifica que:
1. El nombre del bucket es correcto
2. La ruta del archivo es correcta (incluye la carpeta si la hay)
3. El archivo existe: `gsutil ls gs://advseg-data-bucket/datos/`

## 📝 Notas Importantes

- El archivo se cachea en la aplicación, así que cambios en Cloud Storage no se reflejan hasta que reinicies la sesión
- Puedes subir múltiples archivos al bucket y cambiar entre ellos
- Los archivos en Cloud Storage tienen costos de almacenamiento (muy bajos, ~$0.02/GB/mes)

## 🎉 ¡Listo!

Ahora puedes trabajar con archivos de cualquier tamaño. Solo súbelos a Cloud Storage y cárgalos desde la aplicación.

---

**¿Preguntas?** Revisa los logs de la aplicación o los mensajes de error que aparecen en la interfaz.

