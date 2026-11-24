# -*- coding: utf-8 -*-
#
# Descripción: ejecuta los pocos comandos que requieren permisos de root, sin
#              contraseña (ver las reglas que instala autorun.sh en sudoers.d).
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

import logging
import subprocess as sp


def _correr(comando, espera):
    # Sesión propia y sin entrada: dentro de startx la consola es un proceso en
    # segundo plano de la terminal, y sudo no debe intentar usarla.
    return sp.run(comando, stdin=sp.DEVNULL, capture_output=True, text=True,
                  timeout=espera, start_new_session=True)


def ejecutar(*comando, sin_sudo=False, espera=30):
    """Devuelve (ok, salida o motivo del error).

    Con sin_sudo=True, si sudo no está autorizado se intenta directamente:
    systemd permite apagar a quien tiene la sesión local activa.
    """
    intentos = [["sudo", "-n", *comando]]
    if sin_sudo:
        intentos.append(list(comando))
    motivo = ""
    for intento in intentos:
        try:
            r = _correr(intento, espera)
        except (OSError, sp.TimeoutExpired) as e:
            motivo = str(e)
        else:
            if r.returncode == 0:
                return True, r.stdout.strip()
            motivo = r.stderr.strip() or f"código {r.returncode}"
        logging.error("falló %s: %s", intento, motivo)
    return False, motivo
