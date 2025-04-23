# Generador de Códigos QR para Excel

Esta aplicación automatiza la generación de códigos QR a partir de enlaces almacenados en un archivo Excel, guarda los códigos como imágenes individuales e inserta estas imágenes directamente en el archivo Excel original.

## Características principales

- Extrae enlaces de la columna "Link" (columna W) de un archivo Excel
- Genera un código QR para cada enlace válido
- Nombra cada imagen QR según el nombre del usuario (columna A)
- Organiza las imágenes en carpetas por fecha y hora de generación
- Inserta automáticamente los códigos QR en la columna X del archivo Excel
- Muestra progreso en tiempo real para seguir el estado del proceso

## Requisitos previos

- **Python 3.7 o superior** - [Descargar Python](https://www.python.org/downloads/)
- **Bibliotecas Python**:
  - pandas
  - openpyxl
  - qrcode
  - pillow (PIL)

## Instalación

### 1. Instalar Python

1. Descarga e instala Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, asegúrate de marcar la opción "Add Python to PATH"
3. Verifica la instalación abriendo un símbolo del sistema o terminal y escribiendo:
   ```
   python --version
   ```

### 2. Descargar el proyecto

1. Descarga los archivos del proyecto en una carpeta de tu elección
2. Los archivos principales son:
   - `generador_qr_app.py` (script principal)
   - `requirements.txt` (lista de dependencias)

### 3. Crear un entorno virtual (opcional pero recomendado)

```
python -m venv venv
```

Activa el entorno virtual:
- En Windows:
  ```
  .\venv\Scripts\activate
  ```
- En macOS/Linux:
  ```
  source venv/bin/activate
  ```

### 4. Instalar dependencias

```
pip install -r requirements.txt
```

## Uso

### Preparación del archivo Excel

Asegúrate de que tu archivo Excel (.xlsx o .xls) tenga:
- Nombres de usuarios en la columna A
- Enlaces (URLs) en la columna W

### Ejecución del script

1. Abre una terminal o símbolo del sistema
2. Navega hasta la carpeta donde guardaste el script
3. Ejecuta:
   ```
   python generador_qr_final.py
   ```
4. Cuando se te solicite, ingresa la ruta completa del archivo Excel
5. Espera a que se complete el proceso

### Resultados

Al finalizar, obtendrás:

1. **Una nueva carpeta** dentro de `codigos_qr` con formato `YYYY-MM-DD_HH-MM-SS` que contiene todas las imágenes QR generadas
2. **Un nuevo archivo Excel** con el sufijo "_con_QR" que incluye las imágenes QR insertadas en la columna X

## Funcionamiento detallado

### ¿Qué automatiza?

Este script automatiza todo el proceso de generación de códigos QR, eliminando la necesidad de:
- Generar códigos QR manualmente para cada enlace
- Nombrar y organizar los archivos de imagen
- Insertar manualmente las imágenes en el archivo Excel
- Ajustar el tamaño de las imágenes y celdas

### Proceso paso a paso

1. **Lectura del archivo Excel**:
   - Identifica automáticamente las columnas relevantes (nombres y enlaces)
   - Valida los datos para procesar solo registros válidos

2. **Generación de códigos QR**:
   - Para cada enlace válido, crea un código QR
   - Utiliza un tamaño y formato optimizados para legibilidad

3. **Organización de archivos**:
   - Crea una estructura de carpetas organizada por fecha/hora
   - Limpia los nombres de usuario para generar nombres de archivo válidos

4. **Inserción en Excel**:
   - Abre el archivo Excel original para modificación
   - Inserta cada imagen QR en la celda correspondiente de la columna X
   - Ajusta automáticamente dimensiones de celdas para visualización óptima

5. **Finalización**:
   - Guarda una nueva versión del archivo Excel con las imágenes
   - Presenta un resumen del proceso completado

## Solución de problemas

### Errores comunes

1. **"Python no se reconoce como un comando interno"**:
   - Solución: Reinstala Python y asegúrate de marcar "Add Python to PATH"

2. **"No se encuentra el módulo X"**:
   - Solución: Reinstala las dependencias con `pip install -r requirements.txt`

3. **"No se pudo abrir el archivo Excel"**:
   - Solución: Asegúrate de que el archivo no esté abierto en Excel u otro programa
   - Proporciona la ruta completa al archivo

4. **Imágenes no visibles en Excel**:
   - Solución: Ajusta el zoom o altura de fila en Excel para visualizar correctamente

### Consejos para mejor rendimiento

- Para archivos grandes, el proceso puede tomar varios minutos
- Mantén cerrado el archivo Excel durante el procesamiento
- Los archivos Excel con muchas imágenes pueden volverse más pesados

## Limitaciones actuales

- El script asume que la primera fila contiene encabezados
- Las imágenes se insertan con un tamaño fijo (120x120 píxeles)
- Solo se genera una nueva versión del archivo Excel, no se modifica el original

## Personalización

Si necesitas ajustar parámetros como tamaño de QR o formato de carpetas, puedes modificar el script directamente:

- Para cambiar el tamaño del QR: modifica el parámetro `tamano=10` en la función `generar_qr`
- Para ajustar el tamaño de las imágenes en Excel: modifica los valores `img.width = 120` y `img.height = 120`