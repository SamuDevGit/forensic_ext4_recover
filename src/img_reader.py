import os, struct
class DiskImage:
    def __init__(self, path):
        self.path = path
        self._size = None
        if not os.path.exists(path):
            raise FileNotFoundError(path)
    @property
    def size(self):
        if self._size is None:
            self._size = os.path.getsize(self.path)
        return self._size
    def read(self, offset, size):
        if offset < 0 or size < 0:
            raise ValueError("offset and size must be non-negative")
        with open(self.path, "rb") as f:
            f.seek(offset)
            return f.read(size)
    def read_superblock(self):
        # EXT4 superblock is at offset 1024 and is 1024 bytes long (structure smaller)
        sb_off = 1024
        data = self.read(sb_off, 1024)
        if len(data) < 1024:
            raise ValueError("Image too small to contain ext superblock")
        # parse a few useful fields from ext4 superblock (little endian)
        s = struct.unpack_from("<I"    # s_inodes_count
                               "I"    # s_blocks_count_lo
                               "I"    # s_r_blocks_count_lo
                               "I"    # s_free_blocks_count_lo
                               "I"    # s_free_inodes_count
                               "I"    # s_first_data_block
                               "I"    # s_log_block_size
                               "I"    # s_log_cluster_size
                               "I"    # s_blocks_per_group
                               "I"    # s_clusters_per_group
                               "I"    # s_inodes_per_group
                               "16s"  # s_uuid
                               "60s"  # padding to reach s_magic at offset 56? we'll instead find magic
                               , data, 0)
        # magic is at offset 56 (0x38) as uint16
        s_magic = struct.unpack_from("<H", data, 0x38)[0]
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
