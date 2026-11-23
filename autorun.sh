#!/usr/bin/bash
#

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
  sudo apt install libsdl2-dev libgtkmm-3.0-dev libepoxy-dev meson alsa-oss portaudio19-dev libminizip-dev
  echo -e "[!] Descargando y compilando el emulador"
  sleep 2
  # Snes9x se compila en el home del usuario; retro_console.py espera
  # encontrar el binario en ~/snes9x-1.60/gtk/build/snes9x-gtk
  cd ~/
  # Descarga el código fuente de snes9x
  wget https://github.com/snes9xgit/snes9x/archive/refs/tags/1.60.tar.gz
  # Descomprime el archivo descargado
  tar -xzf 1.60.tar.gz
  # Entra al directorio del proyecto
  cd snes9x-1.60/gtk
  # Configura la compilación con meson
  meson build --buildtype=release --strip
  # Entra al directorio generado por meson
  cd build
  # Compila el proyecto con ninja
  ninja
  echo -e "[+] Emulador instalado correctamente"
}



function preparar_directorios(){
  local repo_dir="$1"
  echo -e "[!] Preparando directorios de ROMs e íconos"

  mkdir -p ~/retro-console/roms ~/retro-console/icons
  cp -n "$repo_dir"/src/icons/*.png ~/retro-console/icons/

  echo -e "[+] Directorios listos en ~/retro-console"
}

function main(){
  local repo_dir="$(pwd)"
  install_python_deps
  snes9x
  preparar_directorios "$repo_dir"
}


main
