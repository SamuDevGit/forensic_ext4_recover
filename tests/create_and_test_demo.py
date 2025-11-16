import os
import subprocess
import sys
import hashlib

# Nombre de la imagen EXT4 que se generará
IMG_NAME = "ext4_test.img"

# Tamaño de la imagen en megabytes (32 MB)
IMG_SIZE_MB = 32

# Punto de montaje donde WSL montará la imagen EXT4
MOUNT_POINT = "/mnt/ext4_demo"

# Diccionario de archivos de prueba que se escribirán dentro del EXT4.
# Luego serán eliminados para simular un escenario forense real.
TEST_FILES = {
    # Archivo PNG pequeño con cabecera válida + datos sintéticos
    "foto.png": b"\x89PNG\x0D\x0A\x1A\x0A" + b"A" * 3000,

    # Imagen JPEG con cabecera válida + datos sintéticos
    "imagen.jpg": b"\xFF\xD8\xFF" + b"B" * 5000,

    # Archivo de texto simple
    "notas.txt": "Este archivo será borrado para la prueba forense.\nLinea 2.\nLinea 3.".encode("utf-8"),
}


def run(cmd):
    """
    Ejecuta un comando en shell (WSL o Windows),
    imprime la salida y devuelve el resultado.

    - shell=True permite usar binarios Linux en WSL.
    - capture_output=True captura stdout y stderr.
    """
    print(f"[CMD] {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Mostrar stdout y stderr si existen
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr)

    return res


def create_image():
    """
    Crea una imagen EXT4 desde cero:
    - Si ya existe, la elimina.
    - Genera un archivo vacío con `dd`.
    - Formatea ese archivo como EXT4 con `mkfs.ext4`.
    """
    print("\n=== CREANDO IMAGEN EXT4 ===")

    # Eliminar imagen anterior si existe
    if os.path.exists(IMG_NAME):
        os.remove(IMG_NAME)

    # Crear archivo vacío con tamaño definido
    run(f"dd if=/dev/zero of={IMG_NAME} bs=1M count={IMG_SIZE_MB}")

    # Formatear archivo como EXT4 con tabla de inodos no lazy
    run(f"mkfs.ext4 -F -E lazy_itable_init=0,lazy_journal_init=0 {IMG_NAME}")

    print(f"[OK] Imagen creada: {IMG_NAME}")


def mount_image():
    """
    Monta la imagen EXT4 en WSL usando loopback.
    Requiere permisos sudo.
    """
    print("\n=== MONTANDO IMAGEN EN WSL ===")

    # Crear carpeta de montaje si no existe
    run(f"sudo mkdir -p {MOUNT_POINT}")

    # Montar la imagen como si fuera un disco real
    run(f"sudo mount -o loop {IMG_NAME} {MOUNT_POINT}")

    print("[OK] Imagen montada en", MOUNT_POINT)


def write_test_files():
    """
    Escribe los archivos definidos en TEST_FILES dentro del sistema EXT4 montado.
    Esto simula actividad real en un disco.
    """
    print("\n=== ESCRIBIENDO ARCHIVOS DE PRUEBA ===")

    for name, data in TEST_FILES.items():
        path = f"{MOUNT_POINT}/{name}"

        # Abrir archivo dentro del EXT4 y escribir el contenido sintético
        with open(path, "wb") as f:
            f.write(data)

        print(f"[OK] Escrito {path} ({len(data)} bytes)")


def delete_test_files():
    """
    Elimina los archivos previamente creados.
    Esto permite que los datos sigan presentes en la imagen,
    pero los inodos y entradas del directorio sean marcados como eliminados,
    creando un escenario perfecto para recuperación forense.
    """
    print("\n=== ELIMINANDO ARCHIVOS DE PRUEBA (PARA FORENSE) ===")

    for name in TEST_FILES.keys():
        path = f"{MOUNT_POINT}/{name}"

        # Borrado usando sudo dentro del EXT4
        run(f"sudo rm {path}")

        print(f"[OK] Archivo borrado: {path}")


def show_inode_info():
    """
    Muestra los inodos asignados mediante `ls -li`,
    importante para saber qué inodos corresponden a los archivos de prueba.
    """
    print("\n=== MOSTRANDO INODOS PARA PRUEBA ===")
    run(f"ls -li {MOUNT_POINT}")


def umount_image():
    """
    Desmonta la imagen EXT4 de WSL.
    Debe hacerse antes de manipular la imagen desde los tests forenses.
    """
    print("\n=== DESMONTANDO IMAGEN ===")

    run(f"sudo umount {MOUNT_POINT}")

    print("[OK] Imagen desmontada")


def print_instructions():
    """
    Muestra instrucciones sobre qué tests ejecutar después de preparar la imagen EXT4.
    """
    print("\n=== INSTRUCCIONES DE USO FORENSE ===")
    print("Ahora puedes correr:\n")
    print("  python3 tests/test_read_inode.py")
    print("  python3 tests/test_extract_blocks.py\n")
    print("O examinar la imagen manualmente con tu CLI:\n")
    print(f"  python3 -m src.cli scan tests/{IMG_NAME} --out scan_results.json\n")
    print("Los archivos fueron escritos, luego borrados.")
    print("Los datos siguen dentro de la imagen y pueden ser recuperados.")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("\n===============================")
    print(" CREACIÓN DE IMAGEN EXT4 DEMO ")
    print("===============================\n")

    # Flujo completo de generación de escenario forense
    create_image()
    mount_image()
    write_test_files()
    show_inode_info()
    delete_test_files()
    umount_image()

    print("\n[OK] Proceso completado. La imagen está lista para análisis forense.\n")

    print_instructions()
