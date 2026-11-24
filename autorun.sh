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
matchbox-window-manager -use_titlebar no &
exec python3 $repo_dir/src/retro_console.py
EOF
  chmod +x ~/.xinitrc

  echo -e "[+] Entorno gráfico configurado. Puede que sea necesario cerrar sesión"
  echo -e "    o reiniciar para que el cambio de grupos surta efecto."
  echo -e "    Después, iniciar la interfaz con: startx"
}

function main(){
  local repo_dir="$(pwd)"
  sudo apt-get update
  install_python_deps
  instalar_emulador
  preparar_directorios "$repo_dir"
  configurar_usb "$repo_dir"
  configurar_entorno_grafico "$repo_dir"
}


main
