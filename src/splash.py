#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Splash de arranque: muestra una imagen a pantalla completa con un fundido
# (negro -> imagen -> negro) mientras, en paralelo, reproduce un sonido de
# arranque. Se ejecuta una sola vez, antes de retro_console.py, y termina
# solo (no requiere ninguna tecla ni botón).

import os
import subprocess as sp
import sys
import tkinter as tk
from PIL import Image, ImageTk

# Imagen de la pantalla de arranque. Primero busca una personalizada en
# ~/retro-console/splash/splash.png; si no existe, usa el placeholder
# incluido en el repositorio.
RUTA_REPO = os.path.dirname(os.path.abspath(__file__))
RUTA_IMAGEN_PERSONALIZADA = os.path.expanduser("~/retro-console/splash/splash.png")
RUTA_IMAGEN_PLACEHOLDER = os.path.join(RUTA_REPO, "assets", "splash.png")

# Sonido de arranque. Todavía no existe un archivo real: se deja la ruta
# lista para cuando se agregue uno (.wav). Si no está, el splash igual se
# muestra, solo que sin audio.
RUTA_SONIDO = os.path.expanduser("~/retro-console/splash/boot.wav")

COLOR_FONDO = (18, 20, 28)  # debe coincidir con COLOR_FONDO de retro_console.py

# Duración de cada etapa del fundido, en milisegundos.
DURACION_FADE_IN = 1200
DURACION_ESPERA = 1500
DURACION_FADE_OUT = 900
INTERVALO_MS = 40
PASOS_FADE_IN = DURACION_FADE_IN // INTERVALO_MS
PASOS_FADE_OUT = DURACION_FADE_OUT // INTERVALO_MS


def reproducir_sonido():
    if not os.path.isfile(RUTA_SONIDO):
        print(f"[!] No hay sonido de arranque en {RUTA_SONIDO}; se omite el audio.")
        return
    try:
        # No bloqueante: el fundido de la imagen avanza en paralelo al audio.
        sp.Popen(["aplay", RUTA_SONIDO], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    except FileNotFoundError:
        print("[!] 'aplay' no está instalado (paquete alsa-utils); se omite el audio.")


def cargar_imagen_base(ancho, alto):
    ruta = RUTA_IMAGEN_PERSONALIZADA if os.path.isfile(RUTA_IMAGEN_PERSONALIZADA) else RUTA_IMAGEN_PLACEHOLDER
    imagen = Image.open(ruta).convert("RGB")

    # Escala la imagen para cubrir toda la pantalla, recortando el sobrante,
    # en vez de deformarla al tamaño exacto del monitor.
    escala = max(ancho / imagen.width, alto / imagen.height)
    nuevo_ancho = int(imagen.width * escala)
    nuevo_alto = int(imagen.height * escala)
    imagen = imagen.resize((nuevo_ancho, nuevo_alto))

    izquierda = (nuevo_ancho - ancho) // 2
    arriba = (nuevo_alto - alto) // 2
    return imagen.crop((izquierda, arriba, izquierda + ancho, arriba + alto))


def main():
    app = tk.Tk()
    # El splash no necesita recibir foco de teclado ni ser gestionado por
    # matchbox: es una pantalla de solo lectura que se cierra sola.
    app.overrideredirect(True)
    ancho = app.winfo_screenwidth()
    alto = app.winfo_screenheight()
    app.geometry(f"{ancho}x{alto}+0+0")
    app.configure(bg="black")

    label = tk.Label(app, bg="black", bd=0, highlightthickness=0)
    label.place(x=0, y=0, width=ancho, height=alto)

    imagen_base = cargar_imagen_base(ancho, alto)
    negro = Image.new("RGB", (ancho, alto), COLOR_FONDO)

    referencias_fotos = []  # evita que el recolector de basura borre las imágenes

    def mostrar_frame(imagen):
        foto = ImageTk.PhotoImage(imagen)
        referencias_fotos.append(foto)
        label.configure(image=foto)

    def fundido(origen, destino, paso, total, al_terminar):
        t = paso / total
        frame = Image.blend(origen, destino, t)
        mostrar_frame(frame)
        if paso < total:
            app.after(INTERVALO_MS, lambda: fundido(origen, destino, paso + 1, total, al_terminar))
        else:
            al_terminar()

    def iniciar_espera():
        app.after(DURACION_ESPERA, iniciar_fade_out)

    def iniciar_fade_out():
        fundido(imagen_base, negro, 0, PASOS_FADE_OUT, app.destroy)

    reproducir_sonido()
    fundido(negro, imagen_base, 0, PASOS_FADE_IN, iniciar_espera)

    app.mainloop()


if __name__ == "__main__":
    main()
