# 📦 Resumen: Bucket Compartido del Proyecto

## 🎯 ¿Dónde se crea el bucket?

El bucket `data_clusters` se crea ejecutando el script:

```bash
./crear_bucket_proyecto.sh
```

Este script:
1. ✅ Crea el bucket `data_clusters` si no existe
2. ✅ Configura la región (us-central1)
3. ✅ Otorga permisos al servicio de Cloud Run
4. ✅ Deja todo listo para que los usuarios suban archivos

**Ubicación:** El bucket se crea en tu proyecto de GCP (`advseg-477918`)

## 📤 ¿Cómo pueden los usuarios subir archivos?

Los usuarios tienen **3 formas** de subir archivos al bucket:

### 🌐 Opción 1: Consola de GCP (Más Fácil)

1. Ve a: https://console.cloud.google.com/storage/browser/data_clusters
2. Haz clic en **"Upload"**
3. Selecciona el archivo CSV
4. Espera a que termine
5. Anota el nombre que aparece (esa es la ruta)
6. Usa esa ruta en la aplicación

**✅ Ventajas:** Interfaz visual, fácil de usar, no necesita instalar nada

### 💻 Opción 2: Línea de Comandos (gsutil)

```bash
# Subir a la raíz
gsutil cp archivo.csv gs://data_clusters/

# Subir a una carpeta
gsutil cp archivo.csv gs://data_clusters/datos/
```

**✅ Ventajas:** Rápido para usuarios técnicos, puede automatizarse

### 📤 Opción 3: Desde la Aplicación (Automático)

1. Selecciona **"⬆️ Subir CSV"** en la app
2. Si el archivo es grande (>25MB), se sube automáticamente
3. Se guarda en `uploads/` con nombre único
4. Se carga automáticamente

**✅ Ventajas:** Todo automático, no necesita saber nada de buckets

## 📋 Estructura del Bucket

```
data_clusters/
├── contacts_campus_Qro_.csv          # Archivos en la raíz
├── uploads/                           # Archivos subidos desde la app
│   ├── 20241112_095136_archivo1.csv
│   └── 20241112_100530_archivo2.csv
└── datos/                            # Archivos organizados manualmente
    └── archivo.csv
```

## 🔧 Configuración Inicial (Solo una vez)

**Para el administrador del proyecto:**

1. **Crear el bucket:**
   ```bash
   ./crear_bucket_proyecto.sh
   ```

2. **Verificar que funciona:**
   ```bash
   gsutil ls gs://data_clusters/
   ```

3. **Listo!** Los usuarios ya pueden subir archivos

## 👥 Para los Usuarios

**No necesitan hacer nada especial:**
- El bucket ya está creado y configurado
- Solo necesitan subir su archivo (cualquiera de las 3 formas)
- En la app, solo necesitan especificar la ruta del archivo

**Ejemplo:**
1. Usuario sube `mi_archivo.csv` desde la consola de GCP
2. El archivo aparece como `mi_archivo.csv` en el bucket
3. En la app, ingresa la ruta: `mi_archivo.csv`
4. ¡Listo!

## 📚 Documentación Completa

- **Guía detallada:** `GUIA_SUBIR_ARCHIVOS_BUCKET.md`
- **Configuración técnica:** `BUCKET_COMPARTIDO_PROYECTO.md`
- **Script de creación:** `crear_bucket_proyecto.sh`

---

**✅ Resumen:** El bucket se crea una vez con el script, y los usuarios pueden subir archivos de 3 formas diferentes. Todo está pre-configurado y listo para usar.

