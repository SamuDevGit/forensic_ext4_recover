# src/reconstructor.py
import os
import hashlib

# ============================================================
# EXTRACCIÓN POR OFFSET (recuperación a partir de un desplazamiento)
# ============================================================

def extract_from_offset(image_path, offset, max_size=10*1024*1024, out_dir="recovered", ext=".bin"):
    """
    Extrae bytes crudos desde un OFFSET específico dentro de la imagen RAW.

    Este método se usa normalmente cuando:
      - el escáner detecta una firma de archivo (PNG/JPG/ZIP)
      - se quieren recuperar bytes sin interpretar el sistema de archivos

    Parámetros:
      image_path : ruta del archivo IMG
      offset     : posición absoluta desde donde empezar a leer
      max_size   : límite superior de bytes a extraer
      out_dir    : carpeta de salida
      ext        : extensión opcional para el archivo recuperado

    Retorna:
      (ruta_archivo_recuperado, sha256_hex)
    """

    os.makedirs(out_dir, exist_ok=True)

    # El archivo de salida lleva por nombre recovered_<offset>.ext
    out_path = os.path.join(out_dir, f"recovered_{offset}{ext}")

    # Abrimos la imagen y el archivo de salida
    with open(image_path, "rb") as fin, open(out_path, "wb") as fout:
        fin.seek(offset)              # Mover puntero al offset deseado
        remaining = max_size
        chunk = 65536                 # Lectura por trozos de 64 KB

        # Bucle de extracción
        while remaining > 0:
            data = fin.read(min(chunk, remaining))
            if not data:
                break
            fout.write(data)
            remaining -= len(data)

    # ------------------------------------------------------------
    # Calcular SHA-256 del archivo recuperado (integridad forense)
    # ------------------------------------------------------------
    h = hashlib.sha256()
    with open(out_path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)

    return out_path, h.hexdigest()



# ============================================================
# EXTRACCIÓN POR LISTA DE BLOQUES (RECUPERACIÓN A PARTIR DE INODOS)
# ============================================================

def extract_from_blocks(image_path, block_list, block_size, out_dir="recovered", filename="recovered_by_inode"):
    """
    Reconstruye un archivo a partir de una LISTA DE BLOQUES ext4.

    Este método es más avanzado porque:
      - Usamos la información interna del inodo (i_block[])
      - Cada puntero indica un bloque físico del archivo
      - Leemos los bloques en orden y reconstruimos el archivo original

    Parámetros:
      image_path : ruta al archivo IMG
      block_list : lista de punteros (enteros) a bloques ext4
      block_size : tamaño de un bloque ext4 (típicamente 4096)
      out_dir    : carpeta donde escribir el archivo reconstruido
      filename   : nombre del archivo resultante

    Retorna:
      (ruta_archivo_recuperado, sha256_hex)

    NOTA:
      - Solo reconstruye bloques directos (MVP).
      - Un valor '0' significa fin de lista (sin bloques indirectos).
    """

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    with open(image_path, "rb") as fin, open(out_path, "wb") as fout:

        # Procesar cada puntero de bloque
        for b in block_list:

            if b == 0:
                # Un bloque nulo indica que no hay más contenido
                break

            # Calcular el offset real dentro de la imagen
            offset = b * block_size

            fin.seek(offset)
            data = fin.read(block_size)

            if not data:
                # Si el bloque no existe (imagen truncada), se aborta
                break

            # Escribimos el bloque físico en el archivo reconstruido
            fout.write(data)

    # ------------------------------------------------------------
    # Calcular SHA-256 del archivo reconstruido
    # ------------------------------------------------------------
    h = hashlib.sha256()
    with open(out_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)

    return out_path, h.hexdigest()
