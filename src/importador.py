# -*- coding: utf-8 -*-
#
# Descripción: detecta memorias USB, las monta en solo lectura y copia sus
#              ROMs sin duplicados. Comunica el avance por una cola; nunca
#              toca la interfaz.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

import hashlib
import os
import shutil
import threading

import privilegios
from emulador import es_rom

AYUDANTE = "/usr/local/sbin/retro-usb"  # ver src/retro-usb.sh


class Resultado:
    def __init__(self):
        self.nuevas = []
        self.duplicadas = []
        self.errores = []


def _encabezado_copiadora(ruta):
    # Algunos volcados de SNES traen 512 bytes extra al inicio; sin ignorarlos,
    # el mismo juego parecería distinto según su formato.
    if ruta.lower().endswith((".smc", ".sfc")) and os.path.getsize(ruta) % 1024 == 512:
        return 512
    return 0


def huella(ruta):
    """SHA-256 del contenido de la ROM: identifica copias con otro nombre."""
    suma = hashlib.sha256()
    with open(ruta, "rb") as f:
        f.seek(_encabezado_copiadora(ruta))
        for bloque in iter(lambda: f.read(1 << 20), b""):
            suma.update(bloque)
    return suma.hexdigest()


def _destino_libre(carpeta, nombre):
    base, extension = os.path.splitext(nombre)
    candidato, n = nombre, 2
    while os.path.exists(os.path.join(carpeta, candidato)):
        candidato = f"{base} ({n}){extension}"
        n += 1
    return os.path.join(carpeta, candidato)


def _copiar(origen, destino):
    # Se copia con nombre temporal: si retiran la USB a la mitad, no queda una
    # ROM incompleta en la galería.
    parcial = destino + ".part"
    try:
        shutil.copyfile(origen, parcial)
        with open(parcial, "rb+") as f:
            os.fsync(f.fileno())
        os.replace(parcial, destino)
    finally:
        if os.path.exists(parcial):
            os.remove(parcial)


def importar(origen, carpeta):
    """Copia a 'carpeta' las ROMs de 'origen' (incluye subcarpetas)."""
    resultado = Resultado()
    os.makedirs(carpeta, exist_ok=True)
    conocidas = set()
    for nombre in os.listdir(carpeta):
        if es_rom(nombre):
            try:
                conocidas.add(huella(os.path.join(carpeta, nombre)))
            except OSError:
                pass  # una ROM local ilegible no impide importar las demás

    def error_al_listar(e):
        resultado.errores.append(str(e))

    for raiz, subcarpetas, archivos in os.walk(origen, onerror=error_al_listar):
        subcarpetas[:] = sorted(s for s in subcarpetas if not s.startswith((".", "$")))
        for nombre in sorted(archivos):
            ruta = os.path.join(raiz, nombre)
            if not es_rom(nombre) or os.path.islink(ruta) or not os.path.isfile(ruta):
                continue
            try:
                h = huella(ruta)
                if h in conocidas:
                    resultado.duplicadas.append(nombre)
                    continue
                destino = _destino_libre(carpeta, nombre)
                _copiar(ruta, destino)
                conocidas.add(h)
                resultado.nuevas.append(os.path.basename(destino))
            except OSError as e:
                resultado.errores.append(f"{nombre}: {e.strerror or e}")
    return resultado


def _ayudante(*args):
    return privilegios.ejecutar(AYUDANTE, *args)


def importar_usb(nodo, carpeta):
    """Monta, importa y siempre desmonta."""
    resultado = Resultado()
    nombre = os.path.basename(nodo)
    try:
        ok, salida = _ayudante("montar", nombre)
        if not ok:
            resultado.errores.append(f"No se pudo leer la memoria USB: {salida}")
            return resultado
        try:
            resultado = importar(salida, carpeta)
        finally:
            _ayudante("desmontar", nombre)
    except OSError as e:
        resultado.errores.append(f"Error al importar: {e}")
    return resultado


def importar_en_hilo(nodo, carpeta, cola):
    def tarea():
        try:
            resultado = importar_usb(nodo, carpeta)
        except Exception as e:  # la pantalla no debe quedarse esperando
            resultado = Resultado()
            resultado.errores.append(f"Error inesperado: {e}")
        cola.put(("usb_lista", resultado))

    threading.Thread(target=tarea, daemon=True).start()


def es_usb_con_archivos(propiedades):
    return (propiedades.get("ID_BUS") == "usb"
            and propiedades.get("ID_FS_USAGE") == "filesystem")


def vigilar(cola):
    """Avisa con ("usb_insertada", nodo) cada vez que se conecta una memoria."""
    import pyudev

    monitor = pyudev.Monitor.from_netlink(pyudev.Context())
    monitor.filter_by(subsystem="block")  # particiones y discos sin particionar

    def al_cambiar(dispositivo):
        if dispositivo.action == "add" and es_usb_con_archivos(dispositivo.properties):
            cola.put(("usb_insertada", dispositivo.device_node))

    observador = pyudev.MonitorObserver(monitor, callback=al_cambiar, daemon=True)
    observador.start()
    return observador
