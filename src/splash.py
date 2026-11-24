#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Descripción: splash de arranque. Cubre la ventana del frontend con una
#              imagen durante 5 segundos mientras se reproduce un sonido, y
#              después se retira para mostrar la galería de juegos.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

import os
import subprocess as sp
import tkinter as tk
from PIL import Image, ImageTk

# Los archivos del repositorio se usan por defecto. Para personalizarlos sin
# tocar el repositorio basta colocar otros en ~/retro-console/splash/.
RUTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
RUTA_PERSONALIZADA = os.path.expanduser("~/retro-console/splash")

DURACION_MS = 5000
# Espera máxima a que la ventana sea visible antes de iniciar de todos modos.
ESPERA_VENTANA_MS = 1500
COLOR_FONDO = "#12141c"  # debe coincidir con COLOR_FONDO de retro_console.py


def buscar_asset(nombre):
    ruta = os.path.join(RUTA_PERSONALIZADA, nombre)
    return ruta if os.path.isfile(ruta) else os.path.join(RUTA_ASSETS, nombre)


def reproducir_sonido():
    """Inicia el sonido sin bloquear. Devuelve el proceso, o None si falla."""
    ruta = buscar_asset("boot.wav")
    if not os.path.isfile(ruta):
        print(f"[!] No existe el sonido de arranque: {ruta}")
        return None
    comando = ["aplay", "-q"]
    # Permite elegir la salida (p. ej. plughw:CARD=vc4hdmi0) si la
    # predeterminada de ALSA no es la correcta.
    salida = os.environ.get("RETRO_CONSOLE_AUDIO")
    if salida:
        comando += ["-D", salida]
    try:
        # Los errores de aplay se dejan visibles para poder diagnosticarlos.
        return sp.Popen(comando + [ruta])
    except OSError as e:
        print(f"[!] No se pudo ejecutar aplay (paquete alsa-utils): {e}")
        return None


def cargar_imagen(ancho, alto):
    # Cubre toda la pantalla recortando el sobrante, sin deformar la imagen.
    imagen = Image.open(buscar_asset("splash.png")).convert("RGB")
    escala = max(ancho / imagen.width, alto / imagen.height)
    nuevo_ancho = max(ancho, round(imagen.width * escala))
    nuevo_alto = max(alto, round(imagen.height * escala))
    imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
    x = (nuevo_ancho - ancho) // 2
    y = (nuevo_alto - alto) // 2
    return imagen.crop((x, y, x + ancho, y + alto))


def mostrar_splash(app, al_terminar):
    """Muestra el splash sobre 'app' y llama a al_terminar() al retirarlo."""
    capa = tk.Label(app, bg=COLOR_FONDO, bd=0, highlightthickness=0)
    try:
        foto = ImageTk.PhotoImage(
            cargar_imagen(app.winfo_screenwidth(), app.winfo_screenheight()),
            master=app,
        )
        capa.configure(image=foto)
        capa.foto = foto  # evita que el recolector de basura la borre
    except Exception as e:
        # Un splash dañado no debe impedir que arranque la consola.
        print(f"[!] No se pudo cargar la imagen del splash: {e}")

    iniciado = False

    def terminar():
        capa.destroy()
        al_terminar()

    def iniciar(_evento=None):
        # Los 5 segundos corren desde que la ventana es visible.
        nonlocal iniciado
        if iniciado:
            return
        iniciado = True
        reproducir_sonido()
        app.after(DURACION_MS, terminar)

    capa.bind("<Map>", iniciar)
    app.after(ESPERA_VENTANA_MS, iniciar)
    capa.place(x=0, y=0, relwidth=1, relheight=1)
    capa.lift()
