# Descripción: al iniciar sesión en tty1 abre la consola; en cualquier otra
#              terminal (tty2, SSH) no hace nada. Se instala en
#              /etc/profile.d/retro-console.sh; autorun.sh reemplaza @USUARIO@.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

if [ "$(id -un)" = "@USUARIO@" ] && [ "$(tty)" = "/dev/tty1" ] && [ -z "${DISPLAY:-}" ]; then
  startx -- -nocursor > "$HOME/retro-console/startx.log" 2>&1
  # Si se cierra, getty vuelve a iniciar sesión y la consola reaparece. La
  # pausa evita un ciclo demasiado rápido cuando algo falla.
  sleep 2
  exit
fi
