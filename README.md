#  File System Forensics — EXT4 Recovery Toolkit  
**Recuperación de archivos borrados mediante análisis directo de inodos y bloques EXT4**

Este proyecto implementa una herramienta forense que permite **crear**, **manipular**, **analizar** y **recuperar archivos eliminados** dentro de un sistema de archivos EXT4 utilizando Python y análisis en crudo (raw disk analysis).  

Incluye módulos para la lectura directa de inodos, análisis de superblocks, extracción de bloques y recuperación de datos borrados sin montar el sistema.


## Características Principales

### Crear una imagen EXT4 real para pruebas forenses  
El script `create_and_test_demo.py` genera una imagen EXT4, escribe archivos dentro y luego los elimina, dejando una imagen lista para análisis forense.

### Leer inodos directamente desde la imagen  
`test_read_inode.py` permite inspeccionar metadata:
- Tipo de archivo  
- Tamaño real  
- Punteros de bloques (`i_block`)  
- Información del superblock  
- Descriptor de grupo  
- Offsets reales dentro del archivo RAW  

### Recuperar datos desde bloques asignados  
`test_extract_blocks.py` reconstruye archivos (vivos o borrados) leyendo los bloques originales directamente desde la imagen. (Actualmente no funciona)

### ✔ Uso de Python puro  
El análisis forense se realiza sin montar la imagen, respetando el principio forense de **lectura sin modificación**.

## Estructura del Proyecto

forensic_ext4_recover/
│
├── src/ # Módulos principales
│ ├── cli.py
│ ├── ext4_parser.py # Parser de inodos, superblocks y estructuras EXT4
│ ├── img_reader.py # Lector RAW de offsets y bloques
│ ├── reconstructor.py # Reconstrucción de archivos a partir de bloques
│ ├── unallocated_scanner.py # Escáner de espacio no asignado
│ └── utils.py
│
└── tests/
├── create_and_test_demo.py # Generador de imagen EXT4 + archivos borrados
├── test_read_inode.py # Lectura directa de inodos
├── test_extract_blocks.py # Recuperación por bloques
└── ext4_test.img # Imagen EXT4 generada

## Requisitos

### Para ejecutar todas las funcionalidades del codigo se necesita:

- **WSL** (Ubuntu recomendado)
- **Python 3.10+**
- Herramientas Linux:
  - `dd`
  - `mkfs.ext4`
  - `mount`, `umount`
  - `sudo`

### Python paquetes
Este proyecto no depende de librerías externas.

## Instalación

### 1. Clonar el repositorio:

git clone https://github.com/tuusuario/forensic_ext4_recover.git
cd forensic_ext4_recover

### 2. Entrar a WSL
wsl

### Ejecución de los Tests
A continuación se muestra cómo ejecutar cada uno de los scripts incluidos en la carpeta tests/.

### 1. Crear la imagen EXT4 de prueba
### Este script:

1. Crea ext4_test.img

2. Lo formatea como EXT4

3. Monta la imagen

4. Escribe 3 archivos (png, jpg, txt)

5. Los borra

6. Desmonta el FS

### Ejecutar en WSL:
sudo python3 tests/create_and_test_demo.py

Nota: En el repositorio, el archivo que se crea `ext4_test.img`, con el fin de evitar problemas a la hora de probar la implementacion.

Al final mostrará los números de inodo asignados:

12 foto.png
13 imagen.jpg
14 notas.txt

### 2. Leer un Inodo (Metadata Forense)
### Permite inspeccionar campos internos del inodo:

i_mode (tipo)

i_size

i_block

permisos

timestamps

group descriptors

offset en disco

INODE = 12 (Modificable en funcion de los inodos obtenidos en la creacion de la imagen de prueba)

### Ejecutar en Windows o WSL:
`python3 tests/test_read_inode.py`


3. Recuperar el archivo desde sus bloques
Reconstruye el contenido de un archivo, vivo o borrado, usando sus punteros de bloques.

INODE = 12 (Modificable en funcion de los inodos obtenidos en la creacion de la imagen de prueba)

### Ejecutar:
`python3 tests/test_extract_blocks.py`

### Resultado:
Archivo recuperado: `recovered_inode/inode_12_rec`
SHA-256: 3afa...

El archivo reconstruido se almacena en `recovered_inode/.`

### Flujo de la implementacion:
Crear evidencia: `create_and_test_demo.py`

Identificar inodos: salida de ls -li

Leer el inodo: `test_read_inode.py`

Analizar bloques asignados

Recuperar contenido: `test_extract_blocks.py`

### Explicación Técnica (Resumen)

El proyecto implementa:

Lectura del superblock EXT4 (offset 1024)

Lectura de Group Descriptors

Cálculo de offset para cada inodo

Interpretación del inode structure (256 bytes)

Interpretación de punteros:

bloques directos (0–11)

indirectos (por implementar)

Lectura RAW del disco (sin montar)

Reconstrucción del archivo usando bloques asignados

### Limitaciones Actuales
WSL limpia bloques al borrar → Impide recuperación real.