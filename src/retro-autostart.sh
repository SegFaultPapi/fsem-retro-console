# Descripción: al iniciar sesión en tty1 abre la consola; en cualquier otra
#              terminal (tty2, SSH) no hace nada. Se instala en
#              /etc/profile.d/retro-console.sh y se reemplaza @USUARIO@.
# Autor(es):   Rodríguez Montes de Oca Andrés (SegFaultPapi),
#              Vázquez Martínez Gustavo (snakeassasin6-cell),
#              Sánchez Álvarez Ángel Rubén (Baticonsola)
# Licencia:    MIT (ver LICENSE)

if [ "$(id -un)" = "@USUARIO@" ] && [ "$(tty)" = "/dev/tty1" ] && [ -z "${DISPLAY:-}" ]; then
  retro_inicio=$(date +%s)
  startx -- -nocursor > "$HOME/retro-console/startx.log" 2>&1
  # Si duró poco es que falló: se hace visible la terminal (el arranque limpio
  # la deja en negro) y se muestra el motivo.
  if [ $(( $(date +%s) - retro_inicio )) -lt 10 ]; then
    sudo -n /usr/local/sbin/retro-terminal mostrar
    echo "La consola no pudo iniciar. Se reintentará en 10 segundos."
    echo "Para entrar a una terminal: Ctrl+Alt+F2"
    tail -n 8 "$HOME/retro-console/startx.log"
    sleep 10
  fi
  # Al terminar, getty vuelve a iniciar sesión y la consola reaparece.
  sleep 1
  exit
fi
