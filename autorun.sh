#!/usr/bin/bash
#

function installxbox(){
  echo -e "[!] Instalando dependencias para el driver del control Xbox 360"
  sleep 2
  cd ~/ 
  sudo apt-get install -y \
   g++ \
   libboost-dev \
   scons \
   pkg-config \
   libusb-1.0-0-dev \
   git-core \
   libx11-dev \
   libudev-dev \
   x11proto-core-dev \
   libdbus-glib-1-dev \
   scons
  
  pip install evdev
  pip install pyautogui

  echo -e "[!] Clonando el repositorio de xboxdrv"
  sleep 2
  git clone https://github.com/xboxdrv/xboxdrv
  cd xboxdrv
  scons

  echo -e "[+] Driver instalado correctamente"
}

function snes9x (){
  echo -e "[!] Instalando dependencias del emulador"
  sleep 2
  # Dependencias del sistema
  sudo apt install libsdl2-dev libgtkmm-3.0-dev libepoxy-dev meson alsa-oss portaudio19-dev libminizip-dev
  echo -e "[!] Descargando y compilando el emulador"
  sleep 2
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



function main(){
  installxbox
  snes9x
}


main
