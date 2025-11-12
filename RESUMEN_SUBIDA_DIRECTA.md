# ✅ Subida Directa desde la Aplicación - Implementado

## 🎯 Funcionalidad Agregada

Ahora puedes **subir archivos directamente desde la aplicación web** sin necesidad de usar la línea de comandos o la consola de GCP.

## ✨ Cómo Funciona

### Para Archivos Pequeños (<25MB)
- Funciona como antes: subes el archivo y se carga directamente
- Sin cambios en el flujo

### Para Archivos Grandes (>25MB)
1. **Detección automática:** La aplicación detecta que el archivo es grande
2. **Opción automática:** Te ofrece subirlo a Cloud Storage automáticamente
3. **Subida directa:** El archivo se sube desde tu navegador a Cloud Storage
4. **Carga automática:** Una vez subido, se carga automáticamente desde Cloud Storage

## 🚀 Cómo Usar

### Paso 1: Configurar Permisos (Solo una vez)

Ejecuta el script de configuración que ahora incluye permisos de escritura:

```bash
./configurar_cloud_storage.sh
```

Este script ahora otorga:
- ✅ `Storage Object Viewer` (para leer)
- ✅ `Storage Object Creator` (para escribir/subir)

### Paso 2: Subir desde la Aplicación

1. Abre la aplicación Streamlit
2. Selecciona **"⬆️ Subir CSV"**
3. Selecciona tu archivo CSV
4. Si el archivo es grande (>25MB):
   - Verás una advertencia
   - Se activará automáticamente la opción "☁️ Subir a Cloud Storage automáticamente"
   - Ingresa el nombre del bucket (por defecto: `advseg-data-bucket`)
   - La ruta se genera automáticamente, pero puedes cambiarla
5. Haz clic en **"☁️ Subir y Cargar desde Cloud Storage"**
6. ¡Listo! El archivo se sube y carga automáticamente

## 📋 Flujo Completo

```
Usuario selecciona archivo
         ↓
¿Archivo > 25MB?
    ↓           ↓
   NO          SÍ
    ↓           ↓
Carga directa  Ofrece subir a GCS
    ↓           ↓
              Usuario confirma
                 ↓
           Sube a Cloud Storage
                 ↓
           Carga desde GCS
                 ↓
           ✅ Listo
```

## 🔐 Permisos Necesarios

El servicio de Cloud Run necesita:
- `roles/storage.objectViewer` - Para leer archivos
- `roles/storage.objectCreator` - Para subir archivos

El script `configurar_cloud_storage.sh` configura ambos automáticamente.

## 💡 Ventajas

✅ **Todo desde la aplicación** - No necesitas usar gsutil ni la consola  
✅ **Automático** - Detecta archivos grandes y ofrece la solución  
✅ **Fácil** - Solo seleccionar archivo y hacer clic  
✅ **Seguro** - Los archivos se guardan en tu bucket de GCP  
✅ **Persistente** - Los archivos quedan guardados para reutilizar  

## 📝 Notas

- Los archivos se guardan en la carpeta `uploads/` del bucket
- Se genera un nombre único con timestamp para evitar conflictos
- Puedes cambiar la ruta si lo deseas
- Los archivos subidos quedan disponibles para usar después con "☁️ Cargar desde Cloud Storage"

## 🎉 Resultado

Ahora tienes **3 formas de cargar datos**:

1. **📂 Archivo Predeterminado** - Usa el archivo incluido
2. **⬆️ Subir CSV** - Sube directamente (pequeños) o a Cloud Storage (grandes)
3. **☁️ Cargar desde Cloud Storage** - Carga archivos ya subidos previamente

---

**¡Todo listo!** Solo necesitas ejecutar `./configurar_cloud_storage.sh` una vez para dar permisos de escritura, y luego puedes subir archivos directamente desde la aplicación. 🚀

