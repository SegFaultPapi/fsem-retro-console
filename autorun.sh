#!/usr/bin/bash
#
# Descripción: instala y configura la consola en Raspberry Pi OS Lite.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)
#
# Se detiene en el primer error en vez de seguir en silencio (p. ej. un
# "apt install" sin -y que queda esperando confirmación, o una compilación
# que falla): así un paso roto no deja pasos siguientes en un estado
# inconsistente sin que nadie se entere.
set -euo pipefail
set -E  # el aviso también aplica dentro de las funciones
trap 'echo "[X] La instalación se detuvo en la línea $LINENO: $BASH_COMMAND" >&2' ERR

if [ "$(id -u)" -eq 0 ]; then
  echo "[X] Ejecútalo como usuario normal, sin sudo" >&2
  exit 1
fi

function install_python_deps(){
  echo -e "[!] Instalando dependencias de Python y la interfaz gráfica"
  sleep 2
  # Se instalan como paquetes de Debian en vez de con pip: en Raspberry Pi OS
  # (Bookworm/Trixie) "pip install" sin más falla por la protección
  # externally-managed-environment (PEP 668), y estos paquetes ya están
  # empaquetados para apt.
  sudo apt-get install -y \
   python3-tk \
   python3-pil \
   python3-pil.imagetk \
   python3-evdev \
   python3-pyudev

  echo -e "[+] Dependencias de Python instaladas correctamente"
}

function instalar_emulador(){
  echo -e "[!] Instalando Mednafen (NES, SNES y GBA)"
  sudo apt-get install -y mednafen
  if [ ! -x /usr/games/mednafen ] && ! command -v mednafen > /dev/null; then
    echo "[X] Mednafen no quedó instalado" >&2
    exit 1
  fi

  # Mednafen lee el control por /dev/input/jsX (módulo joydev) y, para
  # identificarlo, por /dev/input/eventX (grupo input).
  echo joydev | sudo tee /etc/modules-load.d/retro-console.conf > /dev/null
  sudo usermod -aG input "$USER"
  echo -e "[+] Emulador instalado correctamente"
}

function preparar_directorios(){
  local repo_dir="$1"
  echo -e "[!] Preparando directorios de ROMs, íconos y splash"

  mkdir -p ~/retro-console/roms ~/retro-console/icons ~/retro-console/splash
  cp -n "$repo_dir"/src/icons/*.png ~/retro-console/icons/

  echo -e "[+] Directorios listos en ~/retro-console"
}

function configurar_usb(){
  local repo_dir="$1"
  echo -e "[!] Configurando la importación desde USB"
  sudo apt-get install -y util-linux udev

  # El ayudante queda en una ruta de root: el usuario puede ejecutarlo con
  # sudo, pero no modificarlo.
  sudo install -o root -g root -m 755 "$repo_dir/src/retro-usb.sh" /usr/local/sbin/retro-usb
  local regla
  regla="$(mktemp)"
  echo "$USER ALL=(root) NOPASSWD: /usr/local/sbin/retro-usb" > "$regla"
  sudo visudo -cqf "$regla"
  sudo install -o root -g root -m 440 "$regla" /etc/sudoers.d/retro-usb
  rm -f "$regla"
}

function configurar_entorno_grafico(){
  local repo_dir="$1"
  echo -e "[!] Configurando el entorno gráfico mínimo (sin escritorio)"

  # xserver-xorg-legacy + matchbox-window-manager: lo mínimo para mostrar
  # una ventana a pantalla completa sin ningún escritorio ni gestor de
  # ventanas superpuestas. matchbox solo maximiza y enfoca automáticamente
  # cada ventana (necesario para que el teclado/control lleguen a la app
  # que está al frente), no trae panel, iconos ni multitarea visual.
  sudo apt-get install -y \
   xserver-xorg \
   xserver-xorg-legacy \
   xinit \
   x11-xserver-utils \
   matchbox-window-manager \
   alsa-utils

  # En Raspberry Pi OS (Bookworm/Trixie) con autologin simple, Xorg no
  # arranca por defecto porque no reconoce la sesión como gestionada por
  # logind; esto le permite a cualquier usuario local iniciar Xorg.
  sudo tee /etc/X11/Xwrapper.config > /dev/null <<'EOF'
allowed_users=anybody
needs_root_rights=yes
EOF

  # El usuario necesita pertenecer a estos grupos para que Xorg pueda
  # abrir la terminal virtual (/dev/tty0) y los dispositivos de video.
  sudo usermod -aG tty,video,audio "$USER"

  cat > ~/.xinitrc <<EOF
#!/bin/sh
# La pantalla no debe apagarse: sin teclado no habría cómo despertarla.
xset s off -dpms
matchbox-window-manager -use_titlebar no &
exec python3 $repo_dir/src/retro_console.py
EOF
  chmod +x ~/.xinitrc

  echo -e "[+] Entorno gráfico configurado"
}

function configurar_arranque(){
  local repo_dir="$1"
  local temporal
  echo -e "[!] Configurando el arranque automático"

  # Terminal de mantenimiento (VIEW + MENU durante 5 s).
  sudo apt-get install -y kbd
  sudo install -o root -g root -m 755 "$repo_dir/src/retro-terminal.sh" /usr/local/sbin/retro-terminal

  # Apagar, reiniciar y abrir la terminal desde el menú, sin contraseña.
  temporal="$(mktemp)"
  echo "$USER ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff, /usr/bin/systemctl reboot, /usr/local/sbin/retro-terminal" > "$temporal"
  sudo visudo -cqf "$temporal"
  sudo install -o root -g root -m 440 "$temporal" /etc/sudoers.d/retro-console

  # Autologin en tty1: reproduce el mismo entorno que un startx manual.
  sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
  sudo tee /etc/systemd/system/getty@tty1.service.d/retro-console.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noissue --noclear %I \$TERM
EOF
  sed "s|@USUARIO@|$USER|g" "$repo_dir/src/retro-autostart.sh" > "$temporal"
  sudo install -o root -g root -m 644 "$temporal" /etc/profile.d/retro-console.sh
  rm -f "$temporal"
  touch ~/.hushlogin  # sin mensaje de bienvenida

  # Versiones anteriores usaban un servicio propio: se retira.
  if [ -f /etc/systemd/system/retro-console.service ]; then
    sudo systemctl disable retro-console.service || true
    sudo rm -f /etc/systemd/system/retro-console.service
  fi
  sudo systemctl daemon-reload
  sudo systemctl set-default multi-user.target
  sudo systemctl enable getty@tty1.service

  # Arranque limpio: oculta los mensajes de Linux, el cursor y el arcoíris.
  # La primera vez se guarda una copia con extensión .retro-bak.
  local boot=/boot/firmware
  [ -f "$boot/cmdline.txt" ] || boot=/boot
  if [ -f "$boot/cmdline.txt" ]; then
    [ -f "$boot/cmdline.txt.retro-bak" ] || sudo cp "$boot/cmdline.txt" "$boot/cmdline.txt.retro-bak"
    temporal="$(mktemp)"
    # Debe quedar en una sola línea y conservar root=.
    sed -E '1!d; s/console=tty1/console=tty3/; s/ (splash|plymouth\.[^ ]+)( |$)/ /g' "$boot/cmdline.txt" \
      | tr -d '\n' | sed -E 's/[[:space:]]+$//' > "$temporal"
    local opcion
    for opcion in quiet loglevel=3 logo.nologo vt.global_cursor_default=0 systemd.show_status=false; do
      grep -qE "(^| )${opcion//./\\.}( |$)" "$temporal" || printf ' %s' "$opcion" >> "$temporal"
    done
    echo >> "$temporal"
    if grep -q 'root=' "$temporal"; then
      sudo cp "$temporal" "$boot/cmdline.txt"
    else
      echo "[!] cmdline.txt inesperado; no se modificó"
    fi
    rm -f "$temporal"
  fi
  if [ -f "$boot/config.txt" ] && ! grep -q '^disable_splash=1' "$boot/config.txt"; then
    [ -f "$boot/config.txt.retro-bak" ] || sudo cp "$boot/config.txt" "$boot/config.txt.retro-bak"
    printf '\n[all]\ndisable_splash=1\n' | sudo tee -a "$boot/config.txt" > /dev/null
  fi

  echo -e "[+] Listo. Reinicia con: sudo reboot"
}

function main(){
  # Se puede ejecutar desde cualquier carpeta.
  local repo_dir
  repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  sudo apt-get update
  install_python_deps
  instalar_emulador
  preparar_directorios "$repo_dir"
  configurar_usb "$repo_dir"
  configurar_entorno_grafico "$repo_dir"
  configurar_arranque "$repo_dir"
}


main
