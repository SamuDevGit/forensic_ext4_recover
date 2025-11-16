import argparse, json, os
from .unallocated_scanner import scan_for_signatures
from .reconstructor import extract_from_offset
from .ext4_parser import parse_superblock

# ------------------------------------------------------------
# Comando: SCAN
# Busca firmas de archivos (PNG, JPG, ZIP, etc.) dentro de la
# imagen RAW, incluso en espacio no asignado.
# ------------------------------------------------------------
def cmd_scan(args):
    print(f"Scanning image: {args.image}")

    # Ejecuta el escáner de firmas contra la imagen
    results = scan_for_signatures(args.image)

    print(f"Found {len(results)} candidate signatures.")

    # Muestra cada hallazgo: nombre, offset y extensión esperada
    for r in results:
        print(f"- {r['name']} at offset {r['offset']} (ext {r['ext']})")

    # Si el usuario pidió guardar el resultado en JSON, hacerlo
    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved results to {args.out}")

# ------------------------------------------------------------
# Comando: EXTRACT
# Extrae bytes desde un offset concreto dentro de la imagen.
# Usado para recuperar restos de archivos detectados en 'scan'.
# ------------------------------------------------------------
def cmd_extract(args):
    out_path, sha = extract_from_offset(
        args.image,
        args.offset,
        max_size=args.maxsize,
        out_dir=args.outdir,
        ext=args.ext or ".bin"
    )

    print(f"Extracted to: {out_path}")
    print(f"SHA256: {sha}")

# ------------------------------------------------------------
# Comando: SUPERBLOCK
# Lee y muestra los campos más importantes del superblock EXT4.
# ------------------------------------------------------------
def cmd_superblock(args):
    sb = parse_superblock(args.image)
    print("Superblock summary:")
    for k, v in sb.items():
        print(f"  {k}: {v}")

# ------------------------------------------------------------
# Función principal: parser CLI con subcomandos
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(prog="forensic-tool")
    sub = parser.add_subparsers(dest="cmd")

    # ----------- Comando: scan -----------
    p_scan = sub.add_parser("scan", help="scan image for known signatures")
    p_scan.add_argument("image")           # ruta a la imagen RAW/EXT4
    p_scan.add_argument("--out", help="save JSON results")

    # ----------- Comando: extract --------
    p_extract = sub.add_parser("extract", help="extract bytes from offset")
    p_extract.add_argument("image")            # imagen origen
    p_extract.add_argument("offset", type=int) # offset donde empieza el archivo
    p_extract.add_argument("--maxsize", type=int, default=5*1024*1024) # límite máx.
    p_extract.add_argument("--outdir", default="recovered")            # carpeta salida
    p_extract.add_argument("--ext", default=None)                      # extensión opc.

    # ----------- Comando: superblock -----
    p_sb = sub.add_parser("superblock", help="print ext4 superblock summary")
    p_sb.add_argument("image")

    # Parsear línea de comandos
    args = parser.parse_args()

    # Llamar al comando correspondiente
    if args.cmd == "scan":
        cmd_scan(args)
    elif args.cmd == "extract":
        cmd_extract(args)
    elif args.cmd == "superblock":
        cmd_superblock(args)
    else:
        parser.print_help()

# ------------------------------------------------------------
# Punto de entrada del script
# ------------------------------------------------------------
if __name__ == '__main__':
    main()
