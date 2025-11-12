# 🔧 Solución para Archivos Grandes (Error 413)

## ❌ Problema

Cuando intentas subir un archivo CSV grande, recibes el error:
```
AxiosError: Request failed with status code 413
```

**Causa:** Google Cloud Run tiene un límite de **32MB** para el tamaño del body de las peticiones HTTP. Este es un límite de la plataforma que no se puede cambiar.

## ✅ Soluciones

### Opción 1: Filtrar Datos en HubSpot (Recomendado) ⭐

Antes de exportar desde HubSpot:

1. **Aplicar filtros de fecha:**
   - Exporta solo contactos de los últimos 6-12 meses
   - Esto reduce significativamente el tamaño del archivo

2. **Filtrar por segmento:**
   - Exporta solo los contactos relevantes para tu análisis
   - Por ejemplo: solo contactos activos, solo de cierta región, etc.

3. **Seleccionar columnas específicas:**
   - No exportes todas las columnas disponibles
   - Solo exporta las que necesitas para el análisis

**Resultado:** Archivo más pequeño (< 32MB) que se puede subir sin problemas.

### Opción 2: Dividir el Archivo

Si necesitas analizar todos los datos:

1. **Exporta múltiples archivos:**
   - Archivo 1: Contactos A-M
   - Archivo 2: Contactos N-Z
   - O divide por fecha: Q1, Q2, Q3, Q4

2. **Analiza cada archivo por separado:**
   - Sube y analiza cada archivo individualmente
   - Compara resultados entre segmentos

### Opción 3: Usar Archivo Predeterminado

Si el archivo `contacts_campus_Qro_.csv` ya está incluido en el despliegue:

1. Selecciona **"📂 Usar Archivo Predeterminado"** en la sidebar
2. La aplicación cargará el archivo automáticamente
3. No necesitas subir nada

### Opción 4: Usar Cloud Storage (Avanzado)

Para archivos muy grandes, puedes implementar una solución con Cloud Storage:

1. **Subir archivo a Cloud Storage:**
   ```bash
   gsutil cp archivo.csv gs://tu-bucket/datos/
   ```

2. **Modificar la aplicación** para leer desde Cloud Storage en lugar de upload directo

**Nota:** Esta opción requiere cambios en el código de la aplicación.

## 📊 Tamaños Recomendados

| Tamaño del Archivo | Estado | Recomendación |
|-------------------|--------|---------------|
| < 10MB | ✅ Óptimo | Sube sin problemas |
| 10-25MB | ⚠️ Aceptable | Puede funcionar, pero considera filtrar |
| 25-32MB | ⚠️ Límite | Filtra datos antes de exportar |
| > 32MB | ❌ No funciona | Debes filtrar o dividir el archivo |

## 🔍 Cómo Verificar el Tamaño

```bash
# En Mac/Linux
ls -lh archivo.csv

# En Windows
# Click derecho → Propiedades → Ver tamaño
```

## 💡 Mejores Prácticas

1. **Exporta solo lo necesario:**
   - Filtra por fecha reciente
   - Selecciona solo contactos relevantes
   - Exporta solo columnas necesarias

2. **Optimiza el CSV:**
   - Elimina columnas vacías
   - Limpia datos duplicados antes de exportar

3. **Planifica tus análisis:**
   - Si necesitas datos históricos, divide por períodos
   - Analiza segmentos por separado

## 🛠️ Cambios Realizados

He actualizado la aplicación para:

1. ✅ Mostrar advertencia sobre el límite de tamaño
2. ✅ Mejorar mensajes de error cuando el archivo es muy grande
3. ✅ Proporcionar sugerencias de solución en el error
4. ✅ Configurar límite de Streamlit a 32MB (máximo de Cloud Run)

## 📝 Nota Técnica

El límite de 32MB es de **Google Cloud Run**, no de Streamlit. Aunque aumentemos el límite de Streamlit, Cloud Run rechazará cualquier petición HTTP con body mayor a 32MB.

Para archivos más grandes, la única solución nativa de Cloud Run sería usar **Cloud Storage** con signed URLs, pero esto requiere cambios significativos en la aplicación.

---

**Recomendación:** La solución más práctica es **filtrar los datos en HubSpot** antes de exportar. Esto no solo resuelve el problema técnico, sino que también mejora el rendimiento del análisis. 🚀

