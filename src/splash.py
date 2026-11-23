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
from PIL import Image, ImageDraw, ImageFont, ImageTk

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
DURACION_ESPERA = 5000
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


def marcar_como_placeholder(imagen):
    # Aviso visible de que esta es la imagen de prueba, no el splash final.
    # Solo se dibuja cuando se usa el placeholder del repo, nunca sobre una
    # imagen personalizada puesta en ~/retro-console/splash/splash.png.
    draw = ImageDraw.Draw(imagen)
    texto = "PLACEHOLDER — reemplazar con el splash final"
    try:
        fuente = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20
        )
    except Exception:
        fuente = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto, font=fuente)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (imagen.width - tw) // 2
    y = imagen.height - th - 40

    draw.rectangle([0, y - 12, imagen.width, y + th + 12], fill=(0, 0, 0))
    draw.text((x, y), texto, font=fuente, fill=(255, 210, 80))
    return imagen

def cargar_imagen_base(ancho, alto):
    es_placeholder = not os.path.isfile(RUTA_IMAGEN_PERSONALIZADA)
    ruta = RUTA_IMAGEN_PLACEHOLDER if es_placeholder else RUTA_IMAGEN_PERSONALIZADA
    imagen = Image.open(ruta).convert("RGB")

    # Escala la imagen para cubrir toda la pantalla, recortando el sobrante,
    # en vez de deformarla al tamaño exacto del monitor.
    escala = max(ancho / imagen.width, alto / imagen.height)
    nuevo_ancho = int(imagen.width * escala)
    nuevo_alto = int(imagen.height * escala)
    imagen = imagen.resize((nuevo_ancho, nuevo_alto))

    izquierda = (nuevo_ancho - ancho) // 2
    arriba = (nuevo_alto - alto) // 2
    imagen = imagen.crop((izquierda, arriba, izquierda + ancho, arriba + alto))

    if es_placeholder:
        imagen = marcar_como_placeholder(imagen)

    return imagen


def main():
    app = tk.Tk()
    # "overrideredirect" haría que matchbox-window-manager ignore esta
    # ventana por completo (igual que nos pasó con retro_console.py), lo
    # que puede dejarla mal apilada o invisible. Se usa "-fullscreen" para
    # que matchbox sí la gestione y la muestre al frente.
    app.attributes("-fullscreen", True)
    app.configure(bg="black")
    app.lift()
    app.focus_force()
    ancho = app.winfo_screenwidth()
    alto = app.winfo_screenheight()

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
