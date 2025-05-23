#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generador de Códigos QR con Inserción en Excel
----------------------------------------------
Este script lee un archivo Excel, extrae ID_Unico (columna A),
genera códigos QR para cada ID, los guarda como archivos PNG en una carpeta con
fecha y hora, y además los inserta en la columna QR (columna N) del mismo archivo Excel.
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
    nombre = str(nombre).strip().lower().replace(' ', '_')
    # Eliminar caracteres no alfanuméricos excepto guiones bajos
    nombre = re.sub(r'[^a-z0-9_]', '', nombre)
    return nombre

def generar_qr(texto, nombre_archivo=None, tamano=10, return_image=False):
    """
    Genera un código QR a partir de un texto y lo guarda como archivo PNG.
    
    Args:
        texto (str): Contenido del código QR (ID_Unico)
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
    Lee un archivo Excel, genera códigos QR para cada ID_Unico en la columna A,
    los guarda como archivos PNG y los inserta en la columna N (QR) del Excel.
    
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
        
        # Identificar columna ID_Unico (columna A)
        if 'ID_Unico' in df.columns:
            id_col = 'ID_Unico'
        elif 'Unnamed: 0' in df.columns:  # Primera columna sin nombre
            id_col = 'Unnamed: 0'
        else:
            # Si no encontramos una columna obvia, usamos la primera
            id_col = df.columns[0]
            print(f"Usando columna '{id_col}' para ID_Unico.")
        
        print(f"Usando columna '{id_col}' para generar códigos QR.")
        
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
            
            # Obtener ID_Unico
            id_unico = str(fila[id_col])
            
            # Verificar si hay datos válidos
            if pd.isna(id_unico) or id_unico.strip() == '' or id_unico == 'nan':
                continue
            
            # Limpiar nombre para archivo (usamos el ID_Unico para nombrar el archivo)
            nombre_archivo = limpiar_nombre_archivo(id_unico)
            ruta_archivo_qr = os.path.join(directorio_qr, nombre_archivo)
            
            # Generar código QR usando el ID_Unico como contenido
            resultado = generar_qr(id_unico, ruta_archivo_qr)
            if resultado:
                registros_exitosos += 1
        
        print("\nCódigos QR generados con éxito.")
        print("Insertando códigos QR en el archivo Excel...")
        
        # Ahora, cargar el archivo con openpyxl para manipulación
        wb = openpyxl.load_workbook(ruta_archivo)
        ws = wb.active
        
        # Determinar índice de columna N (QR)
        col_n_index = 14  # Columna N es la 14ª columna (1-indexed)
        
        # Insertar imágenes QR en la columna N
        for row in range(2, total_registros + 2):  # +2 porque Excel es 1-indexed y tiene cabecera
            # Obtener ID_Unico de la columna A
            id_unico = str(ws.cell(row=row, column=1).value)
            # Mostrar progreso
            progreso = (row - 1) / total_registros * 100
            sys.stdout.write(f"\rInsertando en Excel: {row-1}/{total_registros} ({progreso:.1f}%)   ")
            sys.stdout.flush()
            
            if id_unico and id_unico != "None" and id_unico.strip() != '':
                nombre_archivo = limpiar_nombre_archivo(id_unico)
                ruta_qr = os.path.join(directorio_qr, nombre_archivo + ".png")
                
                if os.path.exists(ruta_qr):
                    # Ajustar tamaño de la celda para la imagen
                    ws.row_dimensions[row].height = 120
                    ws.column_dimensions[openpyxl.utils.get_column_letter(col_n_index)].width = 20
                    
                    # Añadir imagen a la celda
                    img = XLImage(ruta_qr)
                    # Ajustar tamaño de la imagen (ancho x alto en pixeles)
                    img.width = 120
                    img.height = 120
                    
                    # Insertamos la imagen en la celda N correspondiente
                    cell = ws.cell(row=row, column=col_n_index)
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
    print("GENERADOR DE CÓDIGOS QR DESDE EXCEL CON INSERCIÓN EN COLUMNA N")
    print("=" * 70)
    print("Este script:")
    print("1. Lee un archivo Excel")
    print("2. Genera códigos QR a partir de los ID_Unico en la columna A")
    print("3. Guarda los QR como imágenes PNG en una carpeta con fecha y hora")
    print("4. Inserta los códigos QR en la columna N (QR) del archivo Excel")
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
