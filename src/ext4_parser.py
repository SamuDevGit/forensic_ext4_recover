# src/ext4_parser.py
import struct
from .img_reader import DiskImage

def read_superblock(path):
    """
    Read basic fields from the ext superblock located at absolute offset 1024.
    Returns a dict with common fields (block size, inode size, counts, etc).
    """
    d = DiskImage(path)
    sb = d.read(1024, 1024)
    if len(sb) < 1024:
        raise ValueError("superblock too small or image too small")
    # Fields (offsets are from start of superblock)
    s_inodes_count      = struct.unpack_from("<I", sb, 0)[0]
    s_blocks_count_lo   = struct.unpack_from("<I", sb, 4)[0]
    s_log_block_size    = struct.unpack_from("<I", sb, 24)[0]   # block size = 1024 << s_log_block_size
    s_first_data_block  = struct.unpack_from("<I", sb, 20)[0]
    s_inodes_per_group  = struct.unpack_from("<I", sb, 40)[0]
    s_inode_size        = struct.unpack_from("<H", sb, 88)[0]   # if zero, default 128
    s_magic             = struct.unpack_from("<H", sb, 56)[0]
    block_size = 1024 << s_log_block_size
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

def group_descriptor_table_offset(block_size):
    """
    Conventional location for group descriptor table:
    - if block_size == 1024 -> gd table begins at block 2 (offset 2048)
    - else -> begins at block 1 (offset block_size)
    """
    gd_block = 2 if block_size == 1024 else 1
    return gd_block * block_size

def read_group_descriptor(path, block_size, index=0):
    """
    Read the legacy group descriptor (32-byte) at given index.
    Returns dict with fields bg_block_bitmap, bg_inode_bitmap, bg_inode_table.
    NOTE: does not parse extended 64-bit fields (hi) — MVP keeps legacy fields.
    """
    d = DiskImage(path)
    gd_off = group_descriptor_table_offset(block_size) + index * 32
    data = d.read(gd_off, 32)
    if len(data) < 32:
        raise ValueError("group descriptor area too small")
    # layout (legacy): 0: bg_block_bitmap (4), 4: bg_inode_bitmap (4), 8: bg_inode_table (4), ...
    bg_block_bitmap, bg_inode_bitmap, bg_inode_table = struct.unpack_from("<III", data, 0)
    return {
        "bg_block_bitmap": bg_block_bitmap,
        "bg_inode_bitmap": bg_inode_bitmap,
        "bg_inode_table": bg_inode_table
    }

def read_inode(path, inode_num):
    """
    Read inode by number (1-based).
    - Supports only inodes located in group 0 (simple MVP).
    - Returns a dictionary with key inode metadata and list of i_block pointers.
    """
    sb = read_superblock(path)
    block_size = sb["s_block_size"]
    inode_size = sb["s_inode_size"]
    inodes_per_group = sb["s_inodes_per_group"]
    total_inodes = sb["s_inodes_count"]

    if inode_num < 1 or inode_num > total_inodes:
        raise ValueError("inode number out of range")

    group = (inode_num - 1) // inodes_per_group
    index = (inode_num - 1) % inodes_per_group

    if group != 0:
        raise NotImplementedError("Only group 0 supported in this MVP. Extend to multi-group later.")

    gd = read_group_descriptor(path, block_size, index=0)
    inode_table_block = gd["bg_inode_table"]
    inode_table_offset = inode_table_block * block_size
    inode_offset = inode_table_offset + index * inode_size

    d = DiskImage(path)
    raw = d.read(inode_offset, inode_size)
    if len(raw) < inode_size:
        raise ValueError("inode data incomplete / image truncated")

    # Parse classic inode fields (ext2/3/4 layout)
    i_mode = struct.unpack_from("<H", raw, 0)[0]
    i_uid = struct.unpack_from("<H", raw, 2)[0]
    i_size_lo = struct.unpack_from("<I", raw, 4)[0]
    i_atime = struct.unpack_from("<I", raw, 8)[0]
    i_ctime = struct.unpack_from("<I", raw, 12)[0]
    i_mtime = struct.unpack_from("<I", raw, 16)[0]
    i_dtime = struct.unpack_from("<I", raw, 20)[0]
    i_gid = struct.unpack_from("<H", raw, 24)[0]
    i_links_count = struct.unpack_from("<H", raw, 26)[0]
    i_blocks = struct.unpack_from("<I", raw, 28)[0]
    i_flags = struct.unpack_from("<I", raw, 32)[0]

    # i_block is 15 * 4 bytes starting at offset 40 (0x28)
    i_block = []
    for i in range(15):
        ptr = struct.unpack_from("<I", raw, 40 + i*4)[0]
        i_block.append(ptr)

    # Some ext4 variants store i_size_high at offset 108 (if inode_size large enough)
    i_size_high = 0
    if inode_size >= 0x6c:  # arbitrary check: if inode header long enough
        try:
            i_size_high = struct.unpack_from("<I", raw, 108)[0]
        except struct.error:
            i_size_high = 0

    full_size = (i_size_high << 32) | i_size_lo

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
