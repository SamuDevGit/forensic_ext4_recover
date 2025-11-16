# src/ext4_parser.py
import struct
from .img_reader import DiskImage

# -------------------------------------------------------------------
# SUPERBLOCK
# -------------------------------------------------------------------
def read_superblock(path):
    """
    Lee el superblock clásico de EXT2/EXT3/EXT4, el cual siempre se
    encuentra a partir del offset 1024 dentro de la imagen del disco.

    Retorna un diccionario con:
      - tamaño de bloque
      - tamaño de inodo
      - cantidad total de inodos
      - cantidad total de bloques
      - inodos por grupo
      - número mágico (0xEF53)
    """

    d = DiskImage(path)
    sb = d.read(1024, 1024)  # El superblock ocupa 1024 bytes fijos

    if len(sb) < 1024:
        raise ValueError("superblock too small or image too small")

    # Campos principales del superblock (offsets estándar)
    s_inodes_count      = struct.unpack_from("<I", sb, 0)[0]
    s_blocks_count_lo   = struct.unpack_from("<I", sb, 4)[0]
    # El tamaño de bloque se define como: 1024 << s_log_block_size
    s_log_block_size    = struct.unpack_from("<I", sb, 24)[0]
    s_first_data_block  = struct.unpack_from("<I", sb, 20)[0]
    s_inodes_per_group  = struct.unpack_from("<I", sb, 40)[0]
    # Tamaño del inodo: EXT4 permite tamaños mayores a 128
    s_inode_size        = struct.unpack_from("<H", sb, 88)[0]
    s_magic             = struct.unpack_from("<H", sb, 56)[0]

    # Cálculo del tamaño real del bloque
    block_size = 1024 << s_log_block_size

    # EXT2/3 default: inodes de 128 bytes si el campo no fue configurado
    if s_inode_size == 0:
        s_inode_size = 128

    return {
        "s_inodes_count": s_inodes_count,
        "s_blocks_count_lo": s_blocks_count_lo,
        "s_first_data_block": s_first_data_block,
        "s_log_block_size": s_log_block_size,
        "s_block_size": block_size,
        "s_inodes_per_group": s_inodes_per_group,
        "s_inode_size": s_inode_size,
        "s_magic": hex(s_magic)
    }


# -------------------------------------------------------------------
# GROUP DESCRIPTOR TABLE LOCATION
# -------------------------------------------------------------------
def group_descriptor_table_offset(block_size):
    """
    Determina la ubicación estándar de la tabla de descriptores de grupo
    (Group Descriptor Table) según el tamaño de bloque:

      - block_size == 1024 → comienza en el bloque 2 (offset 2048)
      - block_size > 1024 → comienza en el bloque 1

    Esta es la convención clásica de EXT2/3/4.
    """
    gd_block = 2 if block_size == 1024 else 1
    return gd_block * block_size


# -------------------------------------------------------------------
# GROUP DESCRIPTOR
# -------------------------------------------------------------------
def read_group_descriptor(path, block_size, index=0):
    """
    Lee un descriptor de grupo EXT2/3/4 (formato legacy de 32 bytes).
    Cada descriptor almacena:
      - bg_block_bitmap     → bloque donde está el bitmap de bloques
      - bg_inode_bitmap     → bloque donde está el bitmap de inodos
      - bg_inode_table      → bloque donde comienza la tabla de inodos

    *Esta versión lee solo los primeros 32 bytes (formato clásico).*
    """

    d = DiskImage(path)
    gd_off = group_descriptor_table_offset(block_size) + index * 32
    data = d.read(gd_off, 32)

    if len(data) < 32:
        raise ValueError("group descriptor area too small")

    bg_block_bitmap, bg_inode_bitmap, bg_inode_table = \
        struct.unpack_from("<III", data, 0)

    return {
        "bg_block_bitmap": bg_block_bitmap,
        "bg_inode_bitmap": bg_inode_bitmap,
        "bg_inode_table": bg_inode_table
    }


# -------------------------------------------------------------------
# INODE PARSER
# -------------------------------------------------------------------
def read_inode(path, inode_num):
    """
    Lee un inodo EXT4 a partir de su número (1-based indexing).
    Esta implementación MVP soporta únicamente:
        → inodos dentro del grupo 0

    Pasos:
      1. Leer superblock (para obtener tamaño de bloque e inodo)
      2. Leer descriptor de grupo (localizar tabla de inodos)
      3. Calcular offset absoluto del inodo
      4. Parsear campos estándar del inodo
      5. Parsear la lista i_block (15 punteros)
      6. Combinar i_size_low + i_size_high (EXT4) si aplica
    """

    # --- Leer configuración general del sistema de archivos ---
    sb = read_superblock(path)
    block_size = sb["s_block_size"]
    inode_size = sb["s_inode_size"]
    inodes_per_group = sb["s_inodes_per_group"]
    total_inodes = sb["s_inodes_count"]

    # Validación básica
    if inode_num < 1 or inode_num > total_inodes:
        raise ValueError("inode number out of range")

    # Calcular grupo e índice dentro del grupo
    group = (inode_num - 1) // inodes_per_group
    index = (inode_num - 1) % inodes_per_group

    # MVP → solo se soporta el grupo 0
    if group != 0:
        raise NotImplementedError(
            "Only group 0 supported in this MVP. Extend to multi-group later."
        )

    # Leer descriptor de grupo
    gd = read_group_descriptor(path, block_size, index=0)

    # Localizar la tabla de inodos en la imagen
    inode_table_block = gd["bg_inode_table"]
    inode_table_offset = inode_table_block * block_size

    # Calcular el offset exacto del inodo a leer
    inode_offset = inode_table_offset + index * inode_size

    # Leer bytes del inodo
    d = DiskImage(path)
    raw = d.read(inode_offset, inode_size)

    if len(raw) < inode_size:
        raise ValueError("inode data incomplete / image truncated")

    # ----------------------------------------------------------------
    # CAMPOS DEL INODO (formato EXT2/EXT3/EXT4 clásico)
    # ----------------------------------------------------------------
    i_mode        = struct.unpack_from("<H", raw, 0)[0]
    i_uid         = struct.unpack_from("<H", raw, 2)[0]
    i_size_lo     = struct.unpack_from("<I", raw, 4)[0]
    i_atime       = struct.unpack_from("<I", raw, 8)[0]
    i_ctime       = struct.unpack_from("<I", raw, 12)[0]
    i_mtime       = struct.unpack_from("<I", raw, 16)[0]
    i_dtime       = struct.unpack_from("<I", raw, 20)[0]
    i_gid         = struct.unpack_from("<H", raw, 24)[0]
    i_links_count = struct.unpack_from("<H", raw, 26)[0]
    i_blocks      = struct.unpack_from("<I", raw, 28)[0]
    i_flags       = struct.unpack_from("<I", raw, 32)[0]

    # i_block contiene 15 punteros de 32 bits
    i_block = []
    for i in range(15):
        ptr = struct.unpack_from("<I", raw, 40 + i * 4)[0]
        i_block.append(ptr)

    # EXT4 soporta tamaños mayores con i_size_high
    i_size_high = 0
    if inode_size >= 0x6c:  # inode >= 108 bytes
        try:
            i_size_high = struct.unpack_from("<I", raw, 108)[0]
        except struct.error:
            i_size_high = 0

    full_size = (i_size_high << 32) | i_size_lo

    # Retornar metadatos del inodo
    return {
        "inode_num": inode_num,
        "i_mode": hex(i_mode),
        "i_uid": i_uid,
        "i_gid": i_gid,
        "i_size": full_size,
        "i_links_count": i_links_count,
        "i_blocks": i_blocks,
        "i_flags": hex(i_flags),
        "i_block": i_block,
        "inode_raw_offset": inode_offset,
        "inode_size": inode_size,
        "superblock": sb,
        "group_descriptor": gd
    }
