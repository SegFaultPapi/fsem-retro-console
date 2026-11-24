# -*- coding: utf-8 -*-
#
# Descripción: maneja Mednafen como proceso independiente (iniciar, pausar,
#              reanudar, terminar) y genera el mapeo del gamepad.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

import logging
import os
import shutil
import signal
import subprocess as sp
import time

import control as c

# extensión -> (nombre visible, módulo de Mednafen, puerto del control)
SISTEMAS = {
    ".nes": ("NES", "nes", "port1"),
    ".smc": ("SNES", "snes_faust", "port1"),
    ".sfc": ("SNES", "snes_faust", "port1"),
    ".gba": ("GBA", "gba", "builtin"),
}

# Los botones de acción se asignan por posición física en el SNES; en NES y
# GBA, A del Xbox es A y X es B.
_DOS_BOTONES = {"a": c.BTN_A, "b": c.BTN_X, "select": c.BTN_VIEW, "start": c.BTN_MENU}
BOTONES = {
    "nes": _DOS_BOTONES,
    "gba": {**_DOS_BOTONES, "shoulder_l": c.BTN_LB, "shoulder_r": c.BTN_RB},
    "snes_faust": {
        "b": c.BTN_A, "a": c.BTN_B, "y": c.BTN_X, "x": c.BTN_Y,
        "l": c.BTN_LB, "r": c.BTN_RB, "select": c.BTN_VIEW, "start": c.BTN_MENU,
    },
}
DIRECCIONES = {
    "left": ((c.ABS_HAT0X, "-"), (c.ABS_X, "-")),
    "right": ((c.ABS_HAT0X, "+"), (c.ABS_X, "+")),
    "up": ((c.ABS_HAT0Y, "-"), (c.ABS_Y, "-")),
    "down": ((c.ABS_HAT0Y, "+"), (c.ABS_Y, "+")),
}
CRUCETA_BOTONES = {"up": 544, "down": 545, "left": 546, "right": 547}

BASE = os.path.expanduser("~/retro-console")
TIEMPO_CIERRE = 3.0  # segundos antes de forzar el cierre


def sistema_de(archivo):
    return SISTEMAS.get(os.path.splitext(archivo)[1].lower())


def es_rom(archivo):
    # Los nombres que empiezan con "." son metadatos (p. ej. "._x.nes" de macOS).
    return not archivo.startswith(".") and sistema_de(archivo) is not None


def mapeo_mednafen(mando, modulo, puerto):
    """Argumentos de Mednafen que asignan el control a un módulo.

    Mednafen usa /dev/input/jsX: numera los botones como joydev (primero los
    códigos >= 0x120, después 0x100-0x11f) y los ejes por código ascendente.
    Su ID es bus+vendor+product+version (16 bits c/u), cantidad de ejes,
    cantidad de botones y 32 bits en cero.
    """
    botones = [b for b in mando["botones"] if b >= 0x120]
    botones += [b for b in mando["botones"] if 0x100 <= b < 0x120]
    ejes = mando["ejes"]
    ident = "0x" + "".join(f"{v:04x}" for v in mando["id"])
    ident += f"{len(ejes):04x}{len(botones):04x}" + "0" * 8

    args = []

    def asignar(entrada, origenes):
        if origenes:
            valor = " || ".join(f"joystick {ident} {o}" for o in origenes)
            args.extend([f"-{modulo}.input.{puerto}.gamepad.{entrada}", valor])

    for entrada, codigo in BOTONES[modulo].items():
        asignar(entrada, [f"button_{botones.index(codigo)}"] if codigo in botones else [])
    for entrada, opciones in DIRECCIONES.items():
        origenes = [f"abs_{ejes.index(e)}{signo}" for e, signo in opciones if e in ejes]
        if CRUCETA_BOTONES[entrada] in botones:
            origenes.append(f"button_{botones.index(CRUCETA_BOTONES[entrada])}")
        asignar(entrada, origenes)
    return args


def ruta_mednafen():
    # Debian lo instala en /usr/games, que no siempre está en el PATH.
    return shutil.which("mednafen") or "/usr/games/mednafen"


def ultimo_mensaje():
    """Última línea del registro de Mednafen, para mostrarla en pantalla."""
    try:
        with open(os.path.join(BASE, "mednafen.log"), errors="replace") as f:
            lineas = [l.strip() for l in f if l.strip()]
    except OSError:
        return ""
    return lineas[-1][:90] if lineas else ""


def construir_comando(ruta, mando):
    _nombre, modulo, puerto = sistema_de(ruta)
    # Se usa la salida predeterminada de ALSA, igual que el splash.
    salida = os.environ.get("RETRO_CONSOLE_AUDIO") or "sexyal-literal-default"
    comando = [
        ruta_mednafen(), "-force_module", modulo,
        "-video.fs", "1", f"-{modulo}.stretch", "aspect",
        "-sound.driver", "alsa", "-sound.device", salida,
    ]
    if mando:
        comando += mapeo_mednafen(mando, modulo, puerto)
    return comando + [ruta]


class Emulador:
    """Un solo juego a la vez. Ningún método bloquea la interfaz."""

    def __init__(self):
        self.proceso = None
        self.pausado = False
        self._limite = None

    def iniciar(self, ruta, mando):
        base = os.path.join(BASE, "mednafen")
        os.makedirs(base, exist_ok=True)
        entorno = dict(
            os.environ, MEDNAFEN_HOME=base,
            # Al pausar por USB el juego pierde el foco: no debe minimizarse.
            SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS="0",
        )
        comando = construir_comando(ruta, mando)
        logging.info("ejecutando: %s", comando)
        with open(os.path.join(BASE, "mednafen.log"), "w") as registro:
            self.proceso = sp.Popen(
                comando, env=entorno,
                stdin=sp.DEVNULL, stdout=registro, stderr=sp.STDOUT,
            )
        self.pausado = False
        self._limite = None

    def revisar(self):
        """None si sigue corriendo; si terminó, su código de salida."""
        if self.proceso is None:
            return 0
        codigo = self.proceso.poll()
        if codigo is None:
            if self._limite and time.monotonic() > self._limite:
                self.proceso.kill()
            return None
        self.proceso = None
        logging.info("el emulador terminó con código %s", codigo)
        return codigo

    def _senal(self, senal):
        if self.proceso and self.proceso.poll() is None:
            self.proceso.send_signal(senal)

    def activo(self):
        return self.proceso is not None and self.proceso.poll() is None

    def cerrando(self):
        return self._limite is not None

    def pausar(self):
        self._senal(signal.SIGSTOP)
        self.pausado = True

    def reanudar(self):
        self._senal(signal.SIGCONT)
        self.pausado = False

    def terminar(self):
        """Pide el cierre ordenado (Mednafen guarda la SRAM). Ver revisar()."""
        if self._limite is None:
            self._senal(signal.SIGTERM)
            # Un proceso detenido no atiende SIGTERM hasta reanudarse.
            self.reanudar()
            self._limite = time.monotonic() + TIEMPO_CIERRE
