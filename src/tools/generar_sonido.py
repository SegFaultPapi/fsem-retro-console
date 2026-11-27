#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Descripción: genera src/assets/boot.wav, el sonido original de arranque
#              (arpegio y acorde sintetizados, 5 s). Solo usa la biblioteca
#              estándar; se ejecuta únicamente para regenerar el archivo.
# Autor(es):   Rodríguez Montes de Oca Andrés (SegFaultPapi),
#              Vázquez Martínez Gustavo (snakeassasin6-cell),
#              Sánchez Álvarez Ángel Rubén (Baticonsola)
# Licencia:    MIT (ver LICENSE)

import array
import math
import os
import sys
import wave

FRECUENCIA = 48000
DURACION = 5.0
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "boot.wav")

# (inicio en s, frecuencia en Hz, constante de decaimiento en s, volumen)
NOTAS = [
    (0.15, 220.00, 0.5, 0.5), (0.45, 277.18, 0.5, 0.5),
    (0.75, 329.63, 0.5, 0.5), (1.05, 415.30, 0.5, 0.5),
    (1.50, 110.00, 1.6, 0.6), (1.50, 440.00, 1.4, 0.5),
    (1.50, 554.37, 1.4, 0.4), (1.50, 659.25, 1.4, 0.4),
    (2.10, 880.00, 1.0, 0.25),
]


def main():
    total = int(FRECUENCIA * DURACION)
    mezcla = [0.0] * total
    for inicio, hz, decaimiento, volumen in NOTAS:
        n0 = int(inicio * FRECUENCIA)
        for n in range(n0, total):
            t = (n - n0) / FRECUENCIA
            ataque = min(1.0, t / 0.01)
            fase = 2 * math.pi * hz * t
            onda = math.sin(fase) + math.sin(3 * fase) / 6 + math.sin(5 * fase) / 15
            mezcla[n] += volumen * ataque * math.exp(-t / decaimiento) * onda

    pico = max(abs(v) for v in mezcla)
    muestras = array.array("h")
    for n, v in enumerate(mezcla):
        # Desvanecimiento en los últimos 0.5 s para terminar en silencio.
        salida = min(1.0, (total - 1 - n) / (0.5 * FRECUENCIA))
        valor = int(v / pico * 0.8 * 32767 * salida)
        muestras.extend((valor, valor))  # estéreo: lo requiere el HDMI de la Pi
    if sys.byteorder == "big":
        muestras.byteswap()

    with wave.open(DESTINO, "wb") as archivo:
        archivo.setnchannels(2)
        archivo.setsampwidth(2)
        archivo.setframerate(FRECUENCIA)
        archivo.writeframes(muestras.tobytes())


if __name__ == "__main__":
    main()
