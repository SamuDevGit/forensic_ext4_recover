# tests/test_read_inode.py

import sys, os

# Ajusta el PYTHONPATH para incluir la raíz del proyecto,
# permitiendo importar módulos desde la carpeta src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.ext4_parser import read_inode   # Función encargada de leer un inodo desde una imagen EXT4
import json

# Nombre de la imagen EXT4 previamente generada (por create_and_test_demo.py)
IMAGE = "ext4_test.img"

# Número de inodo a inspeccionar.
# Este valor puede cambiarse según el archivo que quieras analizar.
INODE = 2

print(f"=== Leyendo inodo {INODE} de '{IMAGE}' ===\n")

# ------------------------------------------------------------
# LECTURA DEL INODO COMPLETO
# ------------------------------------------------------------

# read_inode() devuelve un diccionario con:
# - Metadatos del inodo (permisos, UID, tamaño, flags…)
# - Punteros de bloques (i_block)
# - Tamaño de inodo
# - Offset físico dentro de la imagen
# - Superbloque y descriptor de grupo relacionado
inode = read_inode(IMAGE, INODE)

# Imprime toda la estructura del inodo formateada como JSON
print(json.dumps(inode, indent=2))

# ------------------------------------------------------------
# RESUMEN RÁPIDO PARA EL ANÁLISIS FORENSE
# ------------------------------------------------------------

print("\n=== Resumen útil ===")

# Tamaño real del archivo asociado al inodo
print("Tamaño de archivo:", inode["i_size"])

# Lista de punteros a bloques donde se almacena el contenido del archivo
print("Bloques asignados (i_block):", inode["i_block"])

# Tamaño físico de cada bloque en el sistema EXT4
print("Tamaño de bloque:", inode["superblock"]["s_block_size"])
