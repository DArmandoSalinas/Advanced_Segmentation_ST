# 📦 Bucket Compartido del Proyecto - Configuración Simplificada

## 🎯 Solución Implementada

He simplificado la configuración para que **todos los usuarios usen un bucket compartido del proyecto**. Esto hace todo mucho más fácil:

- ✅ **No necesitan crear buckets** - Ya está configurado
- ✅ **No necesitan especificar el bucket** - Está pre-configurado
- ✅ **Solo necesitan la ruta del archivo** - Mucho más simple

## 📋 Configuración

### Bucket del Proyecto

**Nombre del bucket:** `data_clusters`

Este bucket está:
- ✅ Pre-configurado en la aplicación
- ✅ Con permisos ya otorgados al servicio de Cloud Run
- ✅ Listo para que todos los usuarios suban sus archivos

### Estructura del Bucket

```
data_clusters/
├── contacts_campus_Qro_.csv          # Archivos en la raíz
├── uploads/                           # Archivos subidos desde la app
│   ├── 20241112_095136_archivo1.csv
│   └── 20241112_100530_archivo2.csv
└── datos/                            # Archivos organizados manualmente
    └── archivo.csv
```

## 🚀 Cómo Funciona para los Usuarios

### Opción 1: Cargar Archivo Ya Subido

1. Selecciona **"☁️ Cargar desde Cloud Storage"**
2. El bucket `data_clusters` ya está pre-configurado (no necesitas cambiarlo)
3. Solo ingresa la **ruta del archivo**:
   - Si está en la raíz: `contacts_campus_Qro_.csv`
   - Si está en carpeta: `uploads/20241112_095136_archivo.csv`
4. Haz clic en **"Cargar"**

**¡Eso es todo!** No necesitan saber nada sobre buckets.

### Opción 2: Subir Archivo Grande desde la App

1. Selecciona **"⬆️ Subir CSV"**
2. Si el archivo es grande (>25MB), se activa automáticamente la opción de Cloud Storage
3. El bucket `data_clusters` está pre-configurado
4. El archivo se guarda automáticamente en `uploads/` con nombre único
5. Se carga automáticamente

**¡Súper simple!** Todo es automático.

## 🔧 Configuración Técnica

### Variable de Entorno

El bucket se configura mediante la variable de entorno `GCS_BUCKET_NAME`:

```bash
GCS_BUCKET_NAME=data_clusters
```

Esta variable se establece automáticamente en el despliegue (ver `deploy.sh`).

### Cambiar el Bucket (si es necesario)

Si quieres usar un bucket diferente:

1. **Actualizar el despliegue:**
   ```bash
   # Editar deploy.sh y cambiar:
   --set-env-vars="PYARROW_IGNORE_TIMEZONE=1,GCS_BUCKET_NAME=tu-bucket"
   ```

2. **O configurar manualmente:**
   ```bash
   gcloud run services update streamlit-app \
       --set-env-vars="GCS_BUCKET_NAME=tu-bucket" \
       --region us-central1
   ```

## ✅ Ventajas de esta Solución

1. **Simplicidad para usuarios:**
   - No necesitan entender qué es un bucket
   - Solo necesitan la ruta del archivo
   - Todo está pre-configurado

2. **Organización:**
   - Todos los archivos en un solo lugar
   - Fácil de administrar
   - Estructura clara con carpetas

3. **Seguridad:**
   - Permisos centralizados
   - Control desde el proyecto
   - Fácil de auditar

4. **Mantenimiento:**
   - Un solo bucket para configurar
   - Permisos en un solo lugar
   - Más fácil de gestionar

## 📝 Notas Importantes

- **Privacidad:** Todos los usuarios del proyecto pueden ver los archivos en el bucket. Si necesitas privacidad por usuario, considera crear carpetas por usuario o usar buckets separados.

- **Organización:** Los archivos subidos desde la app se guardan automáticamente en `uploads/` con timestamps para evitar conflictos.

- **Permisos:** El servicio de Cloud Run tiene permisos de lectura y escritura en el bucket. Los usuarios no necesitan permisos directos.

## 🎉 Resultado

Ahora es **mucho más simple** para los usuarios:
- ✅ Bucket pre-configurado
- ✅ Solo necesitan la ruta del archivo
- ✅ Todo funciona automáticamente
- ✅ Sin configuración complicada

---

**¡Listo!** La aplicación ahora usa un bucket compartido del proyecto, haciendo todo más simple para los usuarios. 🚀

