# tests/test_extract_blocks.py

import sys, os

# Agrega la carpeta raíz del proyecto al PYTHONPATH para que src/ pueda importarse.
# Esto permite hacer: from src.ext4_parser import ...
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.ext4_parser import read_inode          # Función para leer un inodo desde la imagen EXT4
from src.reconstructor import extract_from_blocks   # Función para reconstruir archivos a partir de bloques

# Nombre de la imagen ext4 previamente generada con create_and_test_demo.py
IMAGE = "ext4_test.img"

# Número de inodo a recuperar.
# Este debe coincidir con uno de los inodos que aparecieron en: ls -li /mnt/ext4_demo
INODE = 12   # Cámbialo según el archivo que quieras recuperar

print(f"=== Recuperación basada en bloques del inodo {INODE} ===\n")

# ------------------------------------------------------------
# LECTURA DEL INODO DESDE LA IMAGEN
# ------------------------------------------------------------

# Obtiene toda la estructura del inodo: tamaño, timestamps, flags y sobre todo sus punteros i_block
inode = read_inode(IMAGE, INODE)

# Lista de punteros a bloques directos / indirectos del inodo
blocks = inode["i_block"]

# Tamaño de bloque del sistema ext4 (1024 / 2048 / 4096)
block_size = inode["superblock"]["s_block_size"]

print("Bloques detectados:", blocks)
print("Tamaño de bloque:", block_size)

# ------------------------------------------------------------
# RECONSTRUCCIÓN DEL ARCHIVO A PARTIR DE SUS BLOQUES
# ------------------------------------------------------------

# Extrae el contenido físico de los bloques del archivo y genera un archivo recuperado.
# - blocks: lista de bloques físicos
# - block_size: tamaño de cada bloque
# - out_dir: carpeta donde se guarda el archivo recuperado
# - filename: nombre base del archivo recuperado
out_path, sha256 = extract_from_blocks(
    IMAGE,
    blocks,
    block_size,
    out_dir="recovered_inode",
    filename=f"inode_{INODE}_rec"
)

# ------------------------------------------------------------
# RESULTADO FINAL
# ------------------------------------------------------------

print("\n=== RESULTADO ===")
print("Archivo recuperado:", out_path)
print("SHA-256:", sha256)
