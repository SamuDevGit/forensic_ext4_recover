import os
import subprocess
import sys
import hashlib

IMG_NAME = "ext4_test.img"
IMG_SIZE_MB = 32   # tamaño de imagen (32 MB)

MOUNT_POINT = "/mnt/ext4_demo"   # punto de montaje en WSL

# Archivos de prueba que se escribirán y luego eliminarán dentro del EXT4
TEST_FILES = {
    "foto.png": b"\x89PNG\x0D\x0A\x1A\x0A" + b"A" * 3000,
    "imagen.jpg": b"\xFF\xD8\xFF" + b"B" * 5000,
    "notas.txt": "Este archivo será borrado para la prueba forense.\nLinea 2.\nLinea 3.".encode("utf-8"),
}

def run(cmd):
    """Ejecuta comando en WSL o Windows y muestra salida."""
    print(f"[CMD] {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout: print(res.stdout)
    if res.stderr: print(res.stderr)
    return res

def create_image():
    print("\n=== CREANDO IMAGEN EXT4 ===")
    if os.path.exists(IMG_NAME):
        os.remove(IMG_NAME)

    run(f"dd if=/dev/zero of={IMG_NAME} bs=1M count={IMG_SIZE_MB}")
    run(f"mkfs.ext4 -F -E lazy_itable_init=0,lazy_journal_init=0 {IMG_NAME}")
    print(f"[OK] Imagen creada: {IMG_NAME}")


def mount_image():
    print("\n=== MONTANDO IMAGEN EN WSL ===")
    run(f"sudo mkdir -p {MOUNT_POINT}")
    run(f"sudo mount -o loop {IMG_NAME} {MOUNT_POINT}")
    print("[OK] Imagen montada en", MOUNT_POINT)


def write_test_files():
    print("\n=== ESCRIBIENDO ARCHIVOS DE PRUEBA ===")
    for name, data in TEST_FILES.items():
        path = f"{MOUNT_POINT}/{name}"
        with open(path, "wb") as f:
            f.write(data)
        print(f"[OK] Escrito {path} ({len(data)} bytes)")


def delete_test_files():
    print("\n=== ELIMINANDO ARCHIVOS DE PRUEBA (PARA FORENSE) ===")
    for name in TEST_FILES.keys():
        path = f"{MOUNT_POINT}/{name}"
        run(f"sudo rm {path}")
        print(f"[OK] Archivo borrado: {path}")


def show_inode_info():
    print("\n=== MOSTRANDO INODOS PARA PRUEBA ===")
    run(f"ls -li {MOUNT_POINT}")


def umount_image():
    print("\n=== DESMONTANDO IMAGEN ===")
    run(f"sudo umount {MOUNT_POINT}")
    print("[OK] Imagen desmontada")


def print_instructions():
    print("\n=== INSTRUCCIONES DE USO FORENSE ===")
    print("Ahora puedes correr:")
    print()
    print("  python3 tests/test_read_inode.py")
    print("  python3 tests/test_extract_blocks.py")
    print()
    print("O examinar la imagen manualmente con tu CLI:")
    print()
    print(f"  python3 -m src.cli scan tests/{IMG_NAME} --out scan_results.json")
    print()
    print("Los archivos fueron escritos, luego borrados.")
    print("Los datos siguen dentro de la imagen y pueden ser recuperados.")


if __name__ == "__main__":
    print("\n===============================")
    print(" CREACIÓN DE IMAGEN EXT4 DEMO ")
    print("===============================\n")

    create_image()
    mount_image()
    write_test_files()
    show_inode_info()
    delete_test_files()
    umount_image()

    print("\n[OK] Proceso completado. La imagen está lista para análisis forense.\n")
    print_instructions()
