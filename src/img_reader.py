import os, struct

class DiskImage:
    """
    Representa una imagen de disco RAW (por ejemplo, un archivo .img).
    Proporciona métodos seguros para:
      - leer por offset
      - obtener tamaño del archivo
      - extraer el superblock EXT4
    """

    def __init__(self, path):
        self.path = path
        self._size = None

        # Verificación básica: ¿el archivo existe?
        if not os.path.exists(path):
            raise FileNotFoundError(path)

    # ------------------------------------------------------------
    # Propiedad: tamaño de la imagen en bytes
    # Se cachea en _size para evitar llamadas repetidas a os.path.getsize.
    # ------------------------------------------------------------
    @property
    def size(self):
        if self._size is None:
            self._size = os.path.getsize(self.path)
        return self._size

    # ------------------------------------------------------------
    # read(offset, size)
    # Lee bytes desde un offset arbitrario de la imagen.
    # Utilizado por el parser EXT4 para leer inodos, bloques, etc.
    # ------------------------------------------------------------
    def read(self, offset, size):
        if offset < 0 or size < 0:
            raise ValueError("offset and size must be non-negative")

        # Abrimos el archivo en modo binario y buscamos el offset exacto
        with open(self.path, "rb") as f:
            f.seek(offset)
            return f.read(size)

    # ------------------------------------------------------------
    # read_superblock()
    # Lee el superblock EXT4 desde offset fijo 1024.
    # Este método incluye un mini-parser minimalista para extraer
    # algunos campos importantes del superblock.
    #
    # NOTA: ext4_parser.py tiene un parser más completo; este es más
    #       simple y sirve como comprobación rápida o fallback.
    # ------------------------------------------------------------
    def read_superblock(self):
        # EXT4: el superblock siempre está en offset 1024
        sb_off = 1024

        # Leemos exactamente 1024 bytes (aunque la estructura interna es más pequeña)
        data = self.read(sb_off, 1024)

        if len(data) < 1024:
            raise ValueError("Image too small to contain ext superblock")

        # Extraemos parte de los campos del superblock usando struct.unpack_from.
        # Esta estructura no es completa, pero obtiene elementos esenciales.
        s = struct.unpack_from(
            "<I"    # s_inodes_count
            "I"     # s_blocks_count_lo
            "I"     # s_r_blocks_count_lo
            "I"     # s_free_blocks_count_lo
            "I"     # s_free_inodes_count
            "I"     # s_first_data_block
            "I"     # s_log_block_size
            "I"     # s_log_cluster_size
            "I"     # s_blocks_per_group
            "I"     # s_clusters_per_group
            "I"     # s_inodes_per_group
            "16s"   # s_uuid (128 bits)
            "60s"   # padding hasta alcanzar s_magic manualmente
            ,
            data, 0
        )

        # EXT4 signature (0xEF53) → offset 56 dentro del superblock
        s_magic = struct.unpack_from("<H", data, 0x38)[0]

        # Retornamos solo los campos más útiles para inspección rápida
        return {
            "s_inodes_count": s[0],
            "s_blocks_count_lo": s[1],
            "s_free_inodes_count": s[4],
            "s_first_data_block": s[5],
            "s_log_block_size": s[6],
            "s_inodes_per_group": s[10],
            "s_uuid": s[11].hex(),
            "s_magic": hex(s_magic)
        }
