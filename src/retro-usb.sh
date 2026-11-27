#!/bin/bash
#
# Descripción: monta y desmonta memorias USB en solo lectura. autorun.sh lo
#              instala en /usr/local/sbin/retro-usb, propiedad de root, y
#              sudoers permite ejecutarlo sin contraseña. Por eso valida todo.
# Autor(es):   Rodríguez Montes de Oca Andrés (SegFaultPapi),
#              Vázquez Martínez Gustavo (snakeassasin6-cell),
#              Sánchez Álvarez Ángel Rubén (Baticonsola)
# Licencia:    MIT (ver LICENSE)

set -euo pipefail
PATH=/usr/sbin:/usr/bin:/sbin:/bin

accion="${1:-}"
nombre="${2:-}"

if [[ ! "$nombre" =~ ^sd[a-z]+[0-9]*$ ]] || [[ ! -b "/dev/$nombre" && "$accion" != desmontar ]]; then
  echo "dispositivo no válido" >&2
  exit 2
fi
punto="/run/retro-usb/$nombre"

case "$accion" in
  montar)
    propiedades="$(udevadm info -q property -n "/dev/$nombre")"
    if ! grep -qx 'ID_BUS=usb' <<< "$propiedades"; then
      echo "no es un dispositivo USB" >&2
      exit 2
    fi
    mkdir -p "$punto"
    if ! mountpoint -q "$punto"; then
      tipo="$(blkid -o value -s TYPE "/dev/$nombre")"
      case "$tipo" in
        # Estos sistemas no guardan permisos: se hacen legibles para todos.
        vfat|exfat|ntfs) mount -t "${tipo/#ntfs/ntfs3}" -o ro,nosuid,nodev,noexec,umask=022 "/dev/$nombre" "$punto" ;;
        ext2|ext3|ext4) mount -t "$tipo" -o ro,nosuid,nodev,noexec "/dev/$nombre" "$punto" ;;
        *) echo "sistema de archivos no soportado: $tipo" >&2; exit 3 ;;
      esac
    fi
    echo "$punto"
    ;;
  desmontar)
    if mountpoint -q "$punto"; then
      # -l: también funciona si ya retiraron la memoria.
      umount "$punto" || umount -l "$punto"
    fi
    rmdir "$punto" 2>/dev/null || true
    ;;
  *)
    echo "uso: retro-usb montar|desmontar sdXN" >&2
    exit 2
    ;;
esac
