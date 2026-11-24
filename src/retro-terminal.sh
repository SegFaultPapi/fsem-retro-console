#!/bin/bash
#
# Descripción: cambia entre la consola y una terminal de mantenimiento (tty2),
#              que pide usuario y contraseña. Se instala como root en
#              /usr/local/sbin/retro-terminal.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

set -euo pipefail
PATH=/usr/sbin:/usr/bin:/sbin:/bin

# El arranque limpio deja la terminal en negro sobre negro: se devuelven los
# colores normales de Linux y el cursor.
mostrar_texto() {
  local p=/sys/module/vt/parameters tty
  echo 0,170,0,170,0,170,0,170,85,255,85,255,85,255,85,255 > "$p/default_red"
  echo 0,0,170,85,0,0,170,170,85,85,255,255,85,85,255,255 > "$p/default_grn"
  echo 0,0,0,0,170,170,170,170,85,85,85,85,255,255,255,255 > "$p/default_blu"
  for tty in "$@"; do
    printf '\033]R\033[?25h' > "$tty"
  done
}

case "${1:-}" in
  abrir)
    mostrar_texto /dev/tty2
    systemctl restart getty@tty2.service
    chvt 2
    ;;
  mostrar)
    # Para diagnóstico: la consola no pudo iniciar.
    mostrar_texto /dev/tty1 /dev/tty2
    ;;
  volver)
    [[ "${2:-}" =~ ^[1-9]$ ]] || { echo "terminal no válida" >&2; exit 2; }
    chvt "$2"
    ;;
  *)
    echo "uso: retro-terminal abrir | mostrar | volver N" >&2
    exit 2
    ;;
esac
