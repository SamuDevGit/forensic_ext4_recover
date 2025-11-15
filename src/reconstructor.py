import os, hashlib
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
    # compute sha256
    sha256 = hashlib.sha256()
    with open(out_path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            sha256.update(b)
    return out_path, sha256.hexdigest()