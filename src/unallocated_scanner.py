import os, struct

# ------------------------------------------------------------
# Lista de firmas mágicas (magic numbers)
# utilizadas para identificar archivos dentro del RAW.
#
# Cada entrada define:
#   - name : nombre del tipo de archivo
#   - sig  : secuencia de bytes característica
#   - ext  : extensión recomendada para la extracción
#
# Este enfoque es típico del file carving forense.
# ------------------------------------------------------------
SIGNATURES = [
    {"name": "PNG",  "sig": b"\x89PNG\r\n\x1a\n", "ext": ".png"},
    {"name": "JPEG", "sig": b"\xff\xd8\xff",      "ext": ".jpg"},
    {"name": "PDF",  "sig": b"%PDF-",             "ext": ".pdf"},
    {"name": "MP3",  "sig": b"ID3",               "ext": ".mp3"},  # Cabecera común de MP3
]


# ------------------------------------------------------------
# scan_for_signatures()
# ------------------------------------------------------------
def scan_for_signatures(image_path, chunk_size=1024*1024):
    """
    Escanea una imagen RAW en búsqueda de firmas binarias conocidas
    (file carving por firmas).

    Retorna una lista de dicts con:
        - name   : tipo de archivo detectado
        - ext    : extensión sugerida
        - offset : posición absoluta en la imagen donde se encontró la firma
        - sig    : firma encontrada en formato hexadecimal

    Parámetros:
      image_path : ruta al archivo IMG o RAW
      chunk_size : tamaño de lectura por bloque (default: 1 MB)

    El escaneo usa ventanas solapadas para evitar que un archivo cuya
    firma esté dividida entre dos chunks quede sin detectar.
    """

    size = os.path.getsize(image_path)
    results = []

    with open(image_path, "rb") as f:
        offset = 0

        # Para evitar perder firmas que caen entre dos lecturas,
        # guardamos los últimos bytes del chunk anterior.
        overlap = 64
        prev = b""

        while True:

            # Leer un trozo grande de la imagen (1 MB por defecto)
            chunk = f.read(chunk_size)
            if not chunk:
                break

            # La ventana contiene:
            #   - últimos 64 bytes del chunk anterior
            #   - chunk actual
            window = prev + chunk

            # Buscar todas las firmas dentro de la ventana
            for sig in SIGNATURES:
                idx = 0
                while True:
                    # Buscar firma dentro de la ventana
                    found = window.find(sig["sig"], idx)
                    if found == -1:
                        break

                    # Calcular offset ABSOLUTO dentro de la imagen
                    absolute = offset - len(prev) + found

                    # Guardar resultado
                    results.append({
                        "name": sig["name"],
                        "ext": sig["ext"],
                        "offset": absolute,
                        "sig": sig["sig"].hex()
                    })

                    # Continuar buscando más instancias
                    idx = found + 1

            # Preparar el solapamiento para la siguiente iteración
            prev = window[-overlap:]
            offset += len(chunk)

    return results
