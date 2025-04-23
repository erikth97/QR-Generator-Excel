#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generador de Códigos QR con Inserción en Excel
----------------------------------------------
Este script lee un archivo Excel, extrae nombres (columna A) y enlaces (columna W),
genera códigos QR para cada enlace, los guarda como archivos PNG en una carpeta con
fecha y hora, y además los inserta en la columna X del mismo archivo Excel.
"""

import os
import re
import pandas as pd
import qrcode
from PIL import Image
import time
import sys
import openpyxl
from openpyxl.drawing.image import Image as XLImage
from datetime import datetime

def limpiar_nombre_archivo(nombre):
    """
    Convierte un nombre a un formato válido para nombre de archivo.
    Reemplaza espacios por guiones bajos y elimina caracteres especiales.
    """
    # Reemplazar espacios por guiones bajos y convertir a minúsculas
    nombre = nombre.strip().lower().replace(' ', '_')
    # Eliminar caracteres no alfanuméricos excepto guiones bajos
    nombre = re.sub(r'[^a-z0-9_]', '', nombre)
    return nombre

def generar_qr(texto, nombre_archivo=None, tamano=10, return_image=False):
    """
    Genera un código QR a partir de un texto y lo guarda como archivo PNG.
    
    Args:
        texto (str): Contenido del código QR (enlace)
        nombre_archivo (str, optional): Nombre del archivo sin extensión
        tamano (int): Tamaño del código QR (1-40)
        return_image (bool): Si es True, devuelve la imagen en memoria
    
    Returns:
        str o Image: Ruta del archivo guardado o imagen en memoria
    """
    try:
        # Crear objeto QR
        qr = qrcode.QRCode(
            version=1,  # Auto ajuste del tamaño
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel bajo de corrección
            box_size=tamano,  # Tamaño de cada "caja" del QR
            border=4,  # Borde alrededor del QR
        )
        
        # Agregar datos
        qr.add_data(texto)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Si necesitamos devolver la imagen en memoria
        if return_image:
            return img
        
        # Si necesitamos guardar en archivo
        if nombre_archivo:
            # Asegurar que el nombre tenga extensión .png
            if not nombre_archivo.lower().endswith('.png'):
                nombre_archivo += '.png'
            
            # Guardar imagen
            img.save(nombre_archivo)
            return nombre_archivo
        
        return None
    except Exception as e:
        print(f"Error al generar QR: {str(e)}")
        return None

def procesar_excel(ruta_archivo):
    """
    Lee un archivo Excel, genera códigos QR para cada enlace en la columna W,
    los guarda como archivos PNG y los inserta en la columna X del Excel.
    
    Args:
        ruta_archivo (str): Ruta al archivo Excel
    """
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            print(f"Error: El archivo {ruta_archivo} no existe.")
            return
        
        # Crear directorio principal para códigos QR si no existe
        directorio_qr_principal = "codigos_qr"
        if not os.path.exists(directorio_qr_principal):
            os.makedirs(directorio_qr_principal)
        
        # Crear subdirectorio con fecha y hora actual
        ahora = datetime.now()
        nombre_subcarpeta = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        directorio_qr = os.path.join(directorio_qr_principal, nombre_subcarpeta)
        os.makedirs(directorio_qr)
        
        # Cargar archivo Excel con pandas para lectura inicial
        print(f"Leyendo archivo {ruta_archivo}...")
        df = pd.read_excel(ruta_archivo)
        
        # Verificar si existen las columnas requeridas
        if 'Unnamed: 0' in df.columns:  # Primera columna sin nombre
            nombres_col = 'Unnamed: 0'
        elif df.columns[0].lower() in ['nombre', 'nombres', 'usuario', 'name']:
            nombres_col = df.columns[0]
        else:
            # Si no encontramos una columna obvia, usamos la primera
            nombres_col = df.columns[0]
            print(f"Usando columna '{nombres_col}' para nombres.")
        
        # Buscar columna W o columna llamada "Link"
        if len(df.columns) >= 23:  # Columna W sería la 23ª columna (0-indexed)
            links_col = df.columns[22]  # Índice 22 corresponde a la columna W
        elif 'Link' in df.columns or 'link' in df.columns or 'URL' in df.columns or 'url' in df.columns:
            links_col = next(col for col in df.columns if col.lower() in ['link', 'url'])
        else:
            print("Error: No se pudo identificar la columna de enlaces (W).")
            return
        
        print(f"Usando columna '{links_col}' para enlaces.")
        
        # Contar registros totales
        total_registros = len(df)
        registros_exitosos = 0
        
        print(f"Procesando {total_registros} registros...")
        
        # Generar códigos QR y guardarlos
        for indice, fila in df.iterrows():
            # Mostrar progreso
            progreso = (indice + 1) / total_registros * 100
            sys.stdout.write(f"\rGenerando QR: {indice + 1}/{total_registros} ({progreso:.1f}%)   ")
            sys.stdout.flush()
            
            # Obtener nombre y enlace
            nombre = str(fila[nombres_col])
            enlace = str(fila[links_col])
            
            # Verificar si hay datos válidos
            if pd.isna(nombre) or pd.isna(enlace) or enlace.strip() == '':
                continue
            
            # Limpiar nombre para archivo
            nombre_archivo = limpiar_nombre_archivo(nombre)
            ruta_archivo_qr = os.path.join(directorio_qr, nombre_archivo)
            
            # Generar código QR
            resultado = generar_qr(enlace, ruta_archivo_qr)
            if resultado:
                registros_exitosos += 1
        
        print("\nCódigos QR generados con éxito.")
        print("Insertando códigos QR en el archivo Excel...")
        
        # Ahora, cargar el archivo con openpyxl para manipulación
        wb = openpyxl.load_workbook(ruta_archivo)
        ws = wb.active
        
        # Determinar índice de columna X
        col_x_index = 24  # Columna X es la 24ª columna (1-indexed)
        
        # Insertar imágenes QR en la columna X
        for row in range(2, total_registros + 2):  # +2 porque Excel es 1-indexed y tiene cabecera
            # Obtener nombre de la columna A
            nombre = str(ws.cell(row=row, column=1).value)
            # Mostrar progreso
            progreso = (row - 1) / total_registros * 100
            sys.stdout.write(f"\rInsertando en Excel: {row-1}/{total_registros} ({progreso:.1f}%)   ")
            sys.stdout.flush()
            
            if nombre and nombre != "None":
                nombre_archivo = limpiar_nombre_archivo(nombre)
                ruta_qr = os.path.join(directorio_qr, nombre_archivo + ".png")
                
                if os.path.exists(ruta_qr):
                    # Ajustar tamaño de la celda para la imagen
                    ws.row_dimensions[row].height = 120
                    ws.column_dimensions[openpyxl.utils.get_column_letter(col_x_index)].width = 20
                    
                    # Añadir imagen a la celda
                    img = XLImage(ruta_qr)
                    # Ajustar tamaño de la imagen (ancho x alto en pixeles)
                    img.width = 120
                    img.height = 120
                    
                    # Insertamos la imagen en la celda X correspondiente
                    cell = ws.cell(row=row, column=col_x_index)
                    ws.add_image(img, cell.coordinate)
        
        # Guardar el archivo Excel con un nuevo nombre
        nombre_base, extension = os.path.splitext(ruta_archivo)
        nuevo_archivo = f"{nombre_base}_con_QR{extension}"
        wb.save(nuevo_archivo)
        
        # Mostrar resumen final
        print(f"\n\nProceso completado:")
        print(f"- {registros_exitosos}/{total_registros} códigos QR generados.")
        print(f"- Los archivos QR se guardaron en: {os.path.abspath(directorio_qr)}")
        print(f"- Archivo Excel con QR guardado como: {nuevo_archivo}")
        
    except Exception as e:
        print(f"\nError al procesar el archivo Excel: {str(e)}")

def main():
    # Mensaje de bienvenida
    print("=" * 70)
    print("GENERADOR DE CÓDIGOS QR DESDE EXCEL CON INSERCIÓN EN COLUMNA X")
    print("=" * 70)
    print("Este script:")
    print("1. Lee un archivo Excel")
    print("2. Genera códigos QR a partir de los enlaces en la columna W")
    print("3. Guarda los QR como imágenes PNG en una carpeta con fecha y hora")
    print("4. Inserta los códigos QR en la columna X del archivo Excel")
    print("=" * 70)
    
    # Solicitar ruta del archivo
    ruta_archivo = input("Ingrese la ruta del archivo Excel (.xlsx): ")
    
    # Validar extensión del archivo
    if not ruta_archivo.lower().endswith(('.xlsx', '.xls')):
        print("Error: El archivo debe tener extensión .xlsx o .xls")
        return
    
    # Procesar archivo
    tiempo_inicio = time.time()
    procesar_excel(ruta_archivo)
    tiempo_total = time.time() - tiempo_inicio
    
    print(f"Tiempo total de procesamiento: {tiempo_total:.2f} segundos")
    print("\nPresione Enter para salir...")
    input()

if __name__ == "__main__":
    main()