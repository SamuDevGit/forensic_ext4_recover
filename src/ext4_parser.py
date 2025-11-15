from .img_reader import DiskImage
# Minimal ext4 parser: currently only exposes superblock parsing via DiskImage.read_superblock()
# Placeholder for future inode/table parsing.
def parse_superblock(path):
    d = DiskImage(path)
    return d.read_superblock()
