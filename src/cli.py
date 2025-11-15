import argparse, json, os
from .unallocated_scanner import scan_for_signatures
from .reconstructor import extract_from_offset
from .ext4_parser import parse_superblock

def cmd_scan(args):
    print(f"Scanning image: {args.image}")
    results = scan_for_signatures(args.image)
    print(f"Found {len(results)} candidate signatures.")
    for r in results:
        print(f"- {r['name']} at offset {r['offset']} (ext {r['ext']})")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved results to {args.out}")

def cmd_extract(args):
    out_path, sha = extract_from_offset(args.image, args.offset, max_size=args.maxsize, out_dir=args.outdir, ext=args.ext or ".bin")
    print(f"Extracted to: {out_path}")
    print(f"SHA256: {sha}")

def cmd_superblock(args):
    sb = parse_superblock(args.image)
    print("Superblock summary:")
    for k,v in sb.items():
        print(f"  {k}: {v}")

def main():
    parser = argparse.ArgumentParser(prog="forensic-tool")
    sub = parser.add_subparsers(dest="cmd")
    p_scan = sub.add_parser("scan", help="scan image for known signatures")
    p_scan.add_argument("image")
    p_scan.add_argument("--out", help="save JSON results")
    p_extract = sub.add_parser("extract", help="extract bytes from offset")
    p_extract.add_argument("image")
    p_extract.add_argument("offset", type=int)
    p_extract.add_argument("--maxsize", type=int, default=5*1024*1024)
    p_extract.add_argument("--outdir", default="recovered")
    p_extract.add_argument("--ext", default=None)
    p_sb = sub.add_parser("superblock", help="print ext4 superblock summary")
    p_sb.add_argument("image")
    args = parser.parse_args()
    if args.cmd == "scan":
        cmd_scan(args)
    elif args.cmd == "extract":
        cmd_extract(args)
    elif args.cmd == "superblock":
        cmd_superblock(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
