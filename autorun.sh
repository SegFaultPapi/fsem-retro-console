#!/usr/bin/bash
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

function snes9x (){
  echo -e "[!] Instalando dependencias del emulador"
  sleep 2
  # Dependencias del sistema
  sudo apt-get install -y \
   libsdl2-dev \
   libgtkmm-3.0-dev \
   libgtk-3-dev \
   libglib2.0-dev \
   libepoxy-dev \
   meson \
   ninja-build \
   alsa-oss \
   portaudio19-dev \
   libminizip-dev

  echo -e "[!] Descargando y compilando el emulador"
  sleep 2
  # Snes9x se compila en el home del usuario; retro_console.py espera
  # encontrar el binario en ~/snes9x-1.60/gtk/build/snes9x-gtk
  cd ~/
  # Descarga el código fuente de snes9x (solo si no se había descargado antes)
  if [ ! -f 1.60.tar.gz ]; then
    wget https://github.com/snes9xgit/snes9x/archive/refs/tags/1.60.tar.gz
  fi
  # Descomprime el archivo descargado
  tar -xzf 1.60.tar.gz
  # Entra al directorio del proyecto
  cd snes9x-1.60/gtk
  # Configura la compilación con meson (se parte de cero por si quedó
  # una carpeta build a medias de un intento anterior fallido).
  # unzip.c (código de 2019, solo se usa para cargar ROMs .zip, que no
  # usamos) no compila con GCC 14 por un cambio de tipo en zlib moderno;
  # se relaja esa advertencia puntual para no bloquear la compilación.
  rm -rf build
  CFLAGS="-Wno-incompatible-pointer-types" meson setup build --buildtype=release --strip
  # Entra al directorio generado por meson
  cd build
  # Compila el proyecto con ninja
  ninja
  echo -e "[+] Emulador instalado correctamente"
}



function preparar_directorios(){
  local repo_dir="$1"
  echo -e "[!] Preparando directorios de ROMs, íconos y splash"

  mkdir -p ~/retro-console/roms ~/retro-console/icons ~/retro-console/splash
  cp -n "$repo_dir"/src/icons/*.png ~/retro-console/icons/

  echo -e "[+] Directorios listos en ~/retro-console"
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
export RETRO_CONSOLE_DEV=1
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
  install_python_deps
  snes9x
  preparar_directorios "$repo_dir"
  configurar_entorno_grafico "$repo_dir"
}


main
