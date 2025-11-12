# 📍 Cómo Identificar la Ruta del Archivo en Cloud Storage

## 🎯 Conceptos Básicos

En Google Cloud Storage, la **ruta del archivo** es simplemente:
- **Si está en la raíz del bucket:** Solo el nombre del archivo
- **Si está en una carpeta:** `carpeta/nombre_archivo.csv` o `carpeta/subcarpeta/nombre_archivo.csv`

## 🔍 Cómo Ver la Ruta en la Consola de GCP

### Opción 1: Desde la Vista de Objetos

1. Ve a [Cloud Storage](https://console.cloud.google.com/storage)
2. Selecciona tu bucket (ej: `data_clusters`)
3. **La ruta es el nombre que aparece en la columna "Name"**

**Ejemplo:**
- Si ves `contacts_campus_Qro_.csv` en la columna "Name" → La ruta es: `contacts_campus_Qro_.csv`
- Si ves `datos/contacts_campus_Qro_.csv` → La ruta es: `datos/contacts_campus_Qro_.csv`

### Opción 2: Desde los Detalles del Archivo

1. Haz clic en el nombre del archivo
2. En la página de detalles, verás:
   - **Bucket:** `data_clusters`
   - **Object name:** `contacts_campus_Qro_.csv` ← **Esta es la ruta**

## 📋 Ejemplos Prácticos

### Caso 1: Archivo en la Raíz del Bucket

**Bucket:** `data_clusters`  
**Nombre del archivo en la lista:** `contacts_campus_Qro_.csv`

**Ruta del archivo:** `contacts_campus_Qro_.csv`

**En la aplicación usarías:**
- Bucket: `data_clusters`
- Ruta: `contacts_campus_Qro_.csv`

### Caso 2: Archivo en una Carpeta

**Bucket:** `data_clusters`  
**Nombre del archivo en la lista:** `uploads/20241112_095136_contacts_campus_Qro_.csv`

**Ruta del archivo:** `uploads/20241112_095136_contacts_campus_Qro_.csv`

**En la aplicación usarías:**
- Bucket: `data_clusters`
- Ruta: `uploads/20241112_095136_contacts_campus_Qro_.csv`

### Caso 3: Archivo en Subcarpeta

**Bucket:** `data_clusters`  
**Nombre del archivo en la lista:** `datos/2024/noviembre/contacts_campus_Qro_.csv`

**Ruta del archivo:** `datos/2024/noviembre/contacts_campus_Qro_.csv`

**En la aplicación usarías:**
- Bucket: `data_clusters`
- Ruta: `datos/2024/noviembre/contacts_campus_Qro_.csv`

## 🖥️ Cómo Ver la Ruta desde la Línea de Comandos

```bash
# Listar archivos en el bucket
gsutil ls gs://data_clusters/

# Listar archivos en una carpeta específica
gsutil ls gs://data_clusters/uploads/

# Ver detalles de un archivo específico
gsutil ls -l gs://data_clusters/contacts_campus_Qro_.csv
```

**La ruta es todo lo que viene después de `gs://nombre-bucket/`**

## ✅ Para tu Caso Específico

Basándome en la imagen que compartiste:

- **Bucket:** `data_clusters`
- **Nombre del archivo:** `contacts_campus_Qro_.csv`
- **Tamaño:** 98.8 MB

**Ruta del archivo:** `contacts_campus_Qro_.csv` (está en la raíz del bucket)

**En la aplicación usarías:**
1. Selecciona **"☁️ Cargar desde Cloud Storage"**
2. **Bucket:** `data_clusters`
3. **Ruta:** `contacts_campus_Qro_.csv`
4. Haz clic en **"🔄 Cargar desde Cloud Storage"**

## 💡 Tips

1. **Copiar la ruta:** En la consola de GCP, puedes hacer clic derecho en el archivo → "Copy gs:// path" y luego quitar `gs://nombre-bucket/` para obtener solo la ruta

2. **Verificar que existe:** Antes de usar en la app, verifica que el archivo existe:
   ```bash
   gsutil ls gs://data_clusters/contacts_campus_Qro_.csv
   ```

3. **Rutas con espacios:** Si el nombre del archivo tiene espacios, úsalo tal cual (Cloud Storage los maneja automáticamente)

4. **Rutas con caracteres especiales:** Si hay caracteres especiales, úsalos tal cual aparecen en la consola

## 🎯 Resumen

**La ruta es simplemente el nombre completo que ves en la columna "Name" de la lista de archivos en Cloud Storage.**

- Si está en la raíz: `nombre_archivo.csv`
- Si está en carpeta: `carpeta/nombre_archivo.csv`
- Si está en subcarpetas: `carpeta/subcarpeta/nombre_archivo.csv`

---

**Para tu archivo específico:**
- Bucket: `data_clusters`
- Ruta: `contacts_campus_Qro_.csv` ✅

