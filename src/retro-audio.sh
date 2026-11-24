#!/bin/bash
#
# Descripción: prepara el jack de 3.5 mm (volumen y silencio) e imprime su
#              dispositivo ALSA. Si no existe, no imprime nada y se usa la
#              salida predeterminada.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

tarjeta="Headphones"
if [ ! -d "/proc/asound/$tarjeta" ]; then
  echo "[!] No se encontró el jack de 3.5 mm; se usa la salida predeterminada" >&2
  exit 0
fi

# El control se llama PCM o Headphone según la versión del kernel.
for control in PCM Headphone; do
  amixer -q -c "$tarjeta" sset "$control" 90% unmute > /dev/null 2>&1
done
echo "plughw:CARD=$tarjeta"
