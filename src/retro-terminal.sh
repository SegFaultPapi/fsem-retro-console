#!/bin/bash
#
# Descripción: cambia entre la consola y una terminal de mantenimiento (tty2),
#              que pide usuario y contraseña. Se instala como root en
#              /usr/local/sbin/retro-terminal.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

set -euo pipefail
PATH=/usr/sbin:/usr/bin:/sbin:/bin

case "${1:-}" in
  abrir)
    systemctl start getty@tty2.service
    # El arranque silencioso oculta el cursor: aquí sí hace falta.
    printf '\033[?25h' > /dev/tty2
    chvt 2
    ;;
  volver)
    [[ "${2:-}" =~ ^[1-9]$ ]] || { echo "terminal no válida" >&2; exit 2; }
    chvt "$2"
    ;;
  *)
    echo "uso: retro-terminal abrir | volver N" >&2
    exit 2
    ;;
esac
