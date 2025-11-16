# tests/test_read_inode.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.ext4_parser import read_inode
import json

IMAGE = "ext4_test.img"
INODE = 2   # Puedes cambiarlo por cualquier otro

print(f"=== Leyendo inodo {INODE} de '{IMAGE}' ===\n")

inode = read_inode(IMAGE, INODE)
print(json.dumps(inode, indent=2))

print("\n=== Resumen útil ===")
print("Tamaño de archivo:", inode["i_size"])
print("Bloques asignados (i_block):", inode["i_block"])
print("Tamaño de bloque:", inode["superblock"]["s_block_size"])
