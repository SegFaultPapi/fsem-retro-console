# -*- coding: utf-8 -*-
#
# Descripción: lectura del gamepad (Xbox One con cable u otro compatible con
#              el mapeo estándar de Linux). Un hilo traduce los eventos a
#              acciones y las deja en una cola; nunca toca la interfaz.
# Autor(es):   Rodríguez Montes de Oca Andrés (SegFaultPapi),
#              Vázquez Martínez Gustavo (snakeassasin6-cell),
#              Sánchez Álvarez Ángel Rubén (Baticonsola)
# Licencia:    MIT (ver LICENSE)

import logging
import threading
import time

# Códigos del kernel (linux/input-event-codes.h), tal como los envía xpad.
EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
SYN_DROPPED = 3
BTN_A, BTN_B, BTN_X, BTN_Y = 304, 305, 307, 308
BTN_LB, BTN_RB, BTN_VIEW, BTN_MENU = 310, 311, 314, 315
ABS_X, ABS_Y, ABS_HAT0X, ABS_HAT0Y = 0, 1, 16, 17

BOTONES = {
    BTN_A: "a", BTN_B: "b",
    544: "arriba", 545: "abajo", 546: "izquierda", 547: "derecha",
}
EJES = {
    ABS_HAT0X: ("izquierda", "derecha"), ABS_HAT0Y: ("arriba", "abajo"),
    ABS_X: ("izquierda", "derecha"), ABS_Y: ("arriba", "abajo"),
}
COMBO_SALIR = {BTN_VIEW, BTN_MENU}

# Fracción del recorrido del stick para activarlo y para soltarlo. Son
# distintas para que una posición intermedia no genere repeticiones.
STICK_ACTIVA, STICK_SUELTA = 0.6, 0.4


class Traductor:
    """Convierte eventos crudos en acciones ('a', 'arriba', 'salir_juego'...)."""

    def __init__(self, rangos_stick=None):
        self.rangos = rangos_stick or {}  # eje -> (mínimo, máximo)
        self.presionados = set()
        self.direccion = {}

    def traducir(self, tipo, codigo, valor):
        if tipo == EV_SYN and codigo == SYN_DROPPED:
            # El kernel descartó eventos: lo que se creía presionado ya no es fiable.
            self.presionados.clear()
            self.direccion.clear()
            return "combo_suelto"
        elif tipo == EV_KEY:
            return self._boton(codigo, valor)
        elif tipo == EV_ABS and codigo in EJES:
            return self._eje(codigo, valor)
        return None

    def _boton(self, codigo, valor):
        if valor == 0:
            completo = COMBO_SALIR <= self.presionados
            self.presionados.discard(codigo)
            return "combo_suelto" if completo and codigo in COMBO_SALIR else None
        if valor != 1:  # repetición automática
            return None
        self.presionados.add(codigo)
        if codigo in COMBO_SALIR and COMBO_SALIR <= self.presionados:
            return "salir_juego"
        return BOTONES.get(codigo)

    def _eje(self, codigo, valor):
        previa = self.direccion.get(codigo, 0)
        if codigo in self.rangos:
            minimo, maximo = self.rangos[codigo]
            mitad = (maximo - minimo) / 2 or 1
            valor = (valor - (minimo + maximo) / 2) / mitad
            umbral = STICK_SUELTA if previa else STICK_ACTIVA
            actual = 0 if abs(valor) < umbral else (1 if valor > 0 else -1)
        else:
            actual = (valor > 0) - (valor < 0)
        self.direccion[codigo] = actual
        if actual == 0 or actual == previa:
            return None
        return EJES[codigo][0 if actual < 0 else 1]


def es_gamepad(botones, ejes):
    """Distingue un gamepad de otros dispositivos con ejes (touchpad, etc.)."""
    direcciones = ABS_HAT0X in ejes or 544 in botones or ABS_X in ejes
    return {BTN_A, BTN_B, BTN_MENU} <= set(botones) and direcciones


class Control(threading.Thread):
    """Busca el gamepad, lo lee y se reconecta si se desenchufa."""

    def __init__(self, cola):
        super().__init__(daemon=True)
        self.cola = cola
        self.descripcion = None  # datos del mando conectado, o None

    def run(self):
        while True:
            dispositivo = self._buscar()
            if dispositivo is None:
                time.sleep(1)
                continue
            try:
                self._leer(dispositivo)
            except OSError as e:
                logging.warning("se perdió el control: %s", e)
            finally:
                self.descripcion = None
                dispositivo.close()
                self.cola.put("desconectado")

    def _buscar(self):
        import evdev

        for ruta in evdev.list_devices():
            try:
                dispositivo = evdev.InputDevice(ruta)
                capacidades = dispositivo.capabilities()
            except OSError:
                continue  # se desconectó entre listarlo y abrirlo
            botones = capacidades.get(EV_KEY, [])
            ejes = dict(capacidades.get(EV_ABS, []))
            if es_gamepad(botones, ejes):
                info = dispositivo.info
                self.descripcion = {
                    "nombre": dispositivo.name,
                    "id": (info.bustype, info.vendor, info.product, info.version),
                    "botones": sorted(botones),
                    "ejes": sorted(ejes),
                }
                self.rangos = {
                    e: (ejes[e].min, ejes[e].max) for e in (ABS_X, ABS_Y) if e in ejes
                }
                return dispositivo
            dispositivo.close()
        return None

    def _leer(self, dispositivo):
        # No se toma en exclusiva (grab): el emulador lee el mismo control.
        logging.info("control detectado: %s", self.descripcion)
        self.cola.put("conectado")
        traductor = Traductor(self.rangos)
        for evento in dispositivo.read_loop():
            accion = traductor.traducir(evento.type, evento.code, evento.value)
            if evento.type == EV_KEY and evento.value == 1:
                logging.info("botón %s -> %s", evento.code, accion)
            if accion:
                self.cola.put(accion)
