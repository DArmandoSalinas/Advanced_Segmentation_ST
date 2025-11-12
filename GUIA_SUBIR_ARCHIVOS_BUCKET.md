# 📤 Guía: Cómo Subir Archivos al Bucket del Proyecto

## 📦 Bucket del Proyecto

**Nombre del bucket:** `data_clusters`

Este es el bucket compartido donde todos los usuarios pueden subir sus archivos CSV para usar en la aplicación.

## 🚀 3 Formas de Subir Archivos

### Opción 1: Desde la Consola de GCP (Más Fácil) ⭐

**Ideal para:** Usuarios que prefieren una interfaz visual

**Pasos:**

1. **Abre la consola de Cloud Storage:**
   - Ve a: https://console.cloud.google.com/storage
   - O busca "Cloud Storage" en la consola de GCP

2. **Selecciona el bucket:**
   - Busca y haz clic en el bucket `data_clusters`
   - Si no lo ves, asegúrate de estar en el proyecto correcto: `advseg-477918`

3. **Sube tu archivo:**
   - Haz clic en el botón **"Upload"** (arriba)
   - Selecciona tu archivo CSV desde tu computadora
   - Haz clic en **"Open"** o **"Abrir"**
   - Espera a que termine la subida

4. **Anota la ruta:**
   - Una vez subido, verás el archivo en la lista
   - **La ruta es el nombre que aparece en la columna "Name"**
   - Ejemplo: Si aparece `contacts_campus_Qro_.csv` → esa es la ruta
   - Si lo subiste a una carpeta: `datos/archivo.csv` → esa es la ruta completa

5. **Usa en la aplicación:**
   - Ve a la aplicación Streamlit
   - Selecciona **"☁️ Cargar desde Cloud Storage"**
   - Ingresa la ruta que anotaste
   - ¡Listo!

**✅ Ventajas:**
- Interfaz visual, fácil de usar
- Puedes ver todos los archivos
- Puedes crear carpetas para organizar
- No necesitas instalar nada

---

### Opción 2: Desde la Línea de Comandos (gsutil)

**Ideal para:** Usuarios técnicos o que prefieren la terminal

**Requisitos:**
- Tener Google Cloud SDK instalado
- Estar autenticado: `gcloud auth login`

**Pasos:**

1. **Autenticarse (si no lo has hecho):**
   ```bash
   gcloud auth login
   gcloud config set project advseg-477918
   ```

2. **Subir archivo a la raíz del bucket:**
   ```bash
   gsutil cp archivo.csv gs://data_clusters/
   ```
   - **Ruta resultante:** `archivo.csv`

3. **Subir archivo a una carpeta específica:**
   ```bash
   gsutil cp archivo.csv gs://data_clusters/datos/
   ```
   - **Ruta resultante:** `datos/archivo.csv`

4. **Verificar que se subió:**
   ```bash
   gsutil ls gs://data_clusters/
   ```

5. **Usa en la aplicación:**
   - Ve a la aplicación Streamlit
   - Selecciona **"☁️ Cargar desde Cloud Storage"**
   - Ingresa la ruta que usaste (ej: `datos/archivo.csv`)
   - ¡Listo!

**✅ Ventajas:**
- Rápido para usuarios técnicos
- Puedes automatizar con scripts
- Útil para múltiples archivos

---

### Opción 3: Desde la Aplicación (Automático) 🎯

**Ideal para:** Cualquier usuario, especialmente para archivos grandes

**Pasos:**

1. **Abre la aplicación Streamlit**

2. **Selecciona "⬆️ Subir CSV"** en la barra lateral

3. **Selecciona tu archivo CSV:**
   - Haz clic en el botón de subir
   - Elige tu archivo desde tu computadora

4. **Si el archivo es grande (>25MB):**
   - La aplicación detecta automáticamente que es grande
   - Se activa la opción **"☁️ Subir a Cloud Storage automáticamente"**
   - El bucket `data_clusters` está pre-configurado
   - El archivo se guarda automáticamente en `uploads/` con nombre único
   - Se carga automáticamente

5. **¡Listo!** El archivo ya está en Cloud Storage y cargado en la aplicación

**✅ Ventajas:**
- Todo automático
- No necesitas saber nada de buckets
- Funciona para archivos de cualquier tamaño
- Los datos quedan guardados para todos los clusters

---

## 📋 Resumen Rápido

| Método | Dificultad | Cuándo Usar |
|--------|-----------|-------------|
| **Consola de GCP** | ⭐ Fácil | Prefieres interfaz visual, quieres organizar archivos |
| **Línea de comandos** | ⭐⭐ Media | Eres técnico, quieres automatizar, múltiples archivos |
| **Desde la app** | ⭐ Muy Fácil | Archivos grandes, quieres que sea automático |

---

## 🔍 Ver Archivos en el Bucket

### Desde la Consola:
1. Ve a: https://console.cloud.google.com/storage/browser/data_clusters
2. Verás todos los archivos y carpetas

### Desde la línea de comandos:
```bash
# Listar todos los archivos
gsutil ls gs://data_clusters/

# Listar archivos en una carpeta
gsutil ls gs://data_clusters/uploads/

# Ver detalles de un archivo
gsutil ls -l gs://data_clusters/archivo.csv
```

---

## 💡 Consejos

1. **Organización:**
   - Puedes crear carpetas para organizar: `datos/`, `usuarios/`, etc.
   - Los archivos subidos desde la app van a `uploads/` automáticamente

2. **Nombres de archivos:**
   - Usa nombres descriptivos: `contactos_2024_noviembre.csv`
   - Evita espacios (usa guiones bajos o guiones)

3. **Rutas:**
   - Si el archivo está en la raíz: solo el nombre → `archivo.csv`
   - Si está en carpeta: incluye la carpeta → `datos/archivo.csv`

4. **Permisos:**
   - Todos los usuarios del proyecto pueden ver y subir archivos
   - El servicio de Cloud Run tiene permisos para leer y escribir

---

## ❓ Preguntas Frecuentes

**¿Necesito permisos especiales?**
- Si estás en el proyecto `advseg-477918`, ya tienes permisos para subir archivos

**¿Puedo borrar archivos?**
- Sí, desde la consola de GCP puedes eliminar archivos que ya no necesites

**¿Hay límite de tamaño?**
- No, Cloud Storage acepta archivos de cualquier tamaño

**¿Los archivos son privados?**
- Los archivos en el bucket son visibles para todos los usuarios del proyecto
- Si necesitas privacidad, considera usar carpetas por usuario

---

## 🎯 Ejemplo Completo

**Escenario:** Quieres subir `contactos_2024.csv` (98MB)

**Opción más fácil:**
1. Ve a: https://console.cloud.google.com/storage/browser/data_clusters
2. Click en "Upload"
3. Selecciona `contactos_2024.csv`
4. Espera a que termine
5. Anota: `contactos_2024.csv` (la ruta)
6. En la app: "☁️ Cargar desde Cloud Storage" → Ruta: `contactos_2024.csv`
7. ¡Listo!

---

**¿Necesitas ayuda?** Revisa la sección "Comenzando" en la aplicación para más detalles.

