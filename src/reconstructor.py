# src/reconstructor.py
import os
import hashlib

# ============================================================
# EXTRACCIÓN POR OFFSET (ya existente)
# ============================================================

def extract_from_offset(image_path, offset, max_size=10*1024*1024, out_dir="recovered", ext=".bin"):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"recovered_{offset}{ext}")

    with open(image_path, "rb") as fin, open(out_path, "wb") as fout:
        fin.seek(offset)
        remaining = max_size
        chunk = 65536

        while remaining > 0:
            data = fin.read(min(chunk, remaining))
            if not data:
                break
            fout.write(data)
            remaining -= len(data)

    # calculate sha256
    h = hashlib.sha256()
    with open(out_path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)

    return out_path, h.hexdigest()



# ============================================================
# EXTRACCIÓN POR LISTA DE BLOQUES (NUEVO)
# ============================================================

def extract_from_blocks(image_path, block_list, block_size, out_dir="recovered", filename="recovered_by_inode"):
    """
    Reconstruye un archivo leyendo bloques físicos en orden desde block_list.
    - block_list: lista de enteros (punteros directos o ya resueltos)
    - block_size: tamaño del bloque ext4 (1024, 2048 o 4096 típicamente)
    - out_dir: carpeta donde se escribirá la recuperación
    - filename: nombre base del archivo reconstruido
    
    Retorna: (ruta_salida, sha256_hex)
    """

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    with open(image_path, "rb") as fin, open(out_path, "wb") as fout:
        for b in block_list:
            if b == 0:
                # Bloque vacío → indica que el archivo termina
                break

            offset = b * block_size
            fin.seek(offset)
            data = fin.read(block_size)

            if not data:
                # Si el bloque no existe físicamente (truncado), se detiene
                break

            fout.write(data)

    # Calcular SHA-256 del archivo reconstruido
    h = hashlib.sha256()
    with open(out_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)

    return out_path, h.hexdigest()
