import os, struct
# Simple signature-based scanner for common file types.
SIGNATURES = [
    {"name":"PNG", "sig":b"\x89PNG\r\n\x1a\n", "ext":".png"},
    {"name":"JPEG", "sig":b"\xff\xd8\xff", "ext":".jpg"},
    {"name":"PDF", "sig":b"%PDF-", "ext":".pdf"},
    {"name":"MP3", "sig":b"ID3", "ext":".mp3"}, # simple
]

def scan_for_signatures(image_path, chunk_size=1024*1024):
    """Scan the raw image for known file signatures. Return list of dicts with offset and signature info."""
    size = os.path.getsize(image_path)
    results = []
    with open(image_path, "rb") as f:
        offset = 0
        # We'll read in overlapping windows to avoid missing signatures crossing boundaries.
        overlap = 64
        prev = b""
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            window = prev + chunk
            for sig in SIGNATURES:
                idx = 0
                while True:
                    found = window.find(sig["sig"], idx)
                    if found == -1:
                        break
                    absolute = offset - len(prev) + found
                    results.append({"name":sig["name"], "ext":sig["ext"], "offset":absolute, "sig":sig["sig"].hex()})
                    idx = found + 1
            # prepare for next iteration
            prev = window[-overlap:]
            offset += len(chunk)
    return results
