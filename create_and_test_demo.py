import os
BASE = os.path.abspath(".")
demo_img = os.path.join(BASE, "demo_disk.img")

# Create demo image with embedded fake PNG and JPEG signatures
with open(demo_img, "wb") as f:
    f.write(b"\x00" * (1024*1024*2))  # 2 MB of zeros
    png_sig = b"\x89PNG\r\n\x1a\n" + b"FAKEPNGDATA" * 50
    f.write(png_sig)
    f.write(b"\x00" * 1024)
    f.write(b"\xff\xd8\xff" + b"FAKEJPG" * 200)
    f.write(b"\x00" * 1024)

print("Demo image created at:", demo_img)
print("Run the scanner like this:")
print(f"  python3 -m src.cli scan {demo_img} --out scan_results.json")
# Example: after you see an offset in scan_results.json, extract:
print("Then extract (example offset):")
print(f"  python3 -m src.cli extract {demo_img} 2097152 --outdir recovered_demo --ext .png")
print("Or view superblock (may raise if not ext4 image):")
print(f"  python3 -m src.cli superblock {demo_img}")
