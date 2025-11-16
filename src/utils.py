import hashlib, os

def sha256_of_file(path):
    """
    Calcula el hash SHA-256 de un archivo, leyéndolo por partes
    para evitar cargarlo completo en memoria.

    Parámetros:
        path : ruta del archivo a hashear

    Retorna:
        Hexstring del hash SHA-256 (64 caracteres)

    Detalles:
    - Se usa lectura en bloques de 64KB para manejar archivos muy grandes.
    - hashlib.sha256() actualiza el estado del hash de manera incremental.
    """

    # Crear objeto SHA-256 vacío
    h = hashlib.sha256()

    # Abrir archivo en modo binario
    with open(path, "rb") as f:

        # Leer en bloques de 65536 bytes (64 KB)
        # iter(...) permite repetir la lectura hasta obtener b"" (EOF)
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)  # Agregar bloque al hash

    # Retornar el hash final en representación hexadecimal
    return h.hexdigest()
