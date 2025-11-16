# tests/test_extract_blocks.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.ext4_parser import read_inode
from src.reconstructor import extract_from_blocks

IMAGE = "ext4_test.img"
INODE = 12   # Cámbialo según el archivo que quieras recuperar

print(f"=== Recuperación basada en bloques del inodo {INODE} ===\n")

# Leer inodo
inode = read_inode(IMAGE, INODE)
blocks = inode["i_block"]
block_size = inode["superblock"]["s_block_size"]

print("Bloques detectados:", blocks)
print("Tamaño de bloque:", block_size)

# Recuperación del archivo desde bloques
out_path, sha256 = extract_from_blocks(
    IMAGE,
    blocks,
    block_size,
    out_dir="recovered_inode",
    filename=f"inode_{INODE}_rec"
)

print("\n=== RESULTADO ===")
print("Archivo recuperado:", out_path)
print("SHA-256:", sha256)
