# FSEm Retro Console

Consola de emulación retro para Raspberry Pi 4, con frontend propio en Python sobre
Raspberry Pi OS Lite. Proyecto final de Fundamentos de Sistemas Embebidos.

- **Repositorio:** https://github.com/SegFaultPapi/fsem-retro-console
- **Video-evidencia:** _pendiente_
- **Autores:** SegFaultPapi · _pendiente: nombres completos del equipo_

## Estado

El prototipo está en desarrollo.

| Función | Estado |
|---|---|
| Splash de 5 s con sonido | Implementado; falta probarlo en la Raspberry Pi |
| Galería con portadas e instrucciones | Implementada |
| Emulación de NES, SNES y GBA (8, 16 y 32 bits) | Implementada con Mednafen; falta probarla en la Raspberry Pi |
| Control con gamepad (menú, juego y salida) | Implementado; falta probarlo en la Raspberry Pi |
| Importación desde USB | Implementada; falta probarla en la Raspberry Pi |
| ROMs precargadas por el instalador | Pendiente |
| Arranque automático (systemd) | Implementado; falta probarlo en la Raspberry Pi |
| Control remoto | Pendiente |

## Materiales

- Raspberry Pi 4 con fuente de alimentación y tarjeta microSD.
- Pantalla HDMI con audio, o bocinas.
- Control de Xbox One con cable USB (o equivalente reconocido por Linux).
- Memoria USB para importar ROMs (opcional).
- Conexión a Internet durante la instalación.

## Descarga e instalación

Desde un Raspberry Pi OS Lite limpio, como usuario normal (el script usa `sudo`):

```bash
sudo apt-get update
sudo apt-get install -y git wget
git clone https://github.com/SegFaultPapi/fsem-retro-console
cd fsem-retro-console
chmod +x autorun.sh
./autorun.sh
sudo reboot
```

`autorun.sh` instala las dependencias, instala Mednafen, crea `~/retro-console`, configura el
entorno gráfico mínimo y **reemplaza `~/.xinitrc`**. Debe ejecutarse desde la raíz del
repositorio. No instala ROMs. `requirements.txt` es solo referencia: no hace falta `pip`.

## ROMs

1. Descargar los juegos desde
   [retrobrews/snes-games](https://github.com/retrobrews/snes-games) o desde la página de
   cada autor en itch.io.
2. Copiar los `.nes`, `.smc`, `.sfc` o `.gba` a `~/retro-console/roms`.
3. Opcional: agregar la portada con el mismo nombre base (`blt.sfc` y `blt.png`).

Este repositorio no distribuye ROMs. Autores y licencias: [`src/THIRD_PARTY.md`](src/THIRD_PARTY.md).
Criterios de selección: [`doc/fuentes-roms.md`](doc/fuentes-roms.md).

## Ejecución

La consola inicia sola al encender. Para mantenimiento, mantener VIEW + MENU
5 segundos en el menú: aparece una terminal que pide usuario y contraseña (requiere teclado).
La misma combinación regresa a la consola. Comandos útiles:

```bash
sudo systemctl stop retro-console       # detener
sudo systemctl restart retro-console    # reiniciar
journalctl -u retro-console -b          # ver errores
```

Para volver al inicio de sesión normal:

```bash
sudo systemctl disable --now retro-console
sudo systemctl enable --now getty@tty1
```

El splash dura 5 segundos y después aparece la galería.

| Acción | Gamepad | Teclado (solo desarrollo) |
|---|---|---|
| Navegar | Cruceta | Flechas |
| Confirmar | A | Enter |
| Cancelar / cerrar la lista de USB | B | No disponible |
| Abrir la terminal / volver a la consola | VIEW + MENU 5 s en el menú | Ctrl+Alt+F2 / Ctrl+Alt+F1 |
| Salir del juego | VIEW + MENU | F12 (Mednafen) |
| Cerrar el programa | No disponible | Esc |

Dentro del juego, VIEW es SELECT y MENU es START. En NES y GBA, A es A y X es B; en SNES los
botones corresponden por posición. El control puede conectarse después de iniciar.

Para probar con teclado: detener el servicio y ejecutar
`RETRO_CONSOLE_DEV=1 startx` desde la consola local.

## Importar ROMs desde USB

1. Conectar la memoria (FAT32, exFAT, NTFS o ext) en el menú o durante una partida.
2. El juego se pausa y las ROMs se copian, incluso desde subcarpetas. La memoria se monta en
   solo lectura.
3. Se muestran las ROMs importadas y las duplicadas. Un duplicado se detecta por el SHA-256 de
   su contenido, aunque tenga otro nombre.
4. Elegir **Continuar juego** o **Volver a los títulos** con la cruceta y A. La memoria ya se
   puede retirar.

## Splash y sonido

Los archivos por defecto están en `src/assets`. Para personalizarlos se colocan `splash.png` y
`boot.wav` en `~/retro-console/splash`. El sonido original se regenera con:

```bash
python3 src/tools/generar_sonido.py
```

## Solución de problemas

- **No se detecta el gamepad:** revisar `lsusb` y `ls /dev/input/by-id/`.
- **Los botones no corresponden:** instalar `evtest`, ejecutar `sudo evtest` y ajustar los
  códigos en `src/control.py`.
- **No hay sonido:** listar salidas con `aplay -L` y probar
  `aplay -D plughw:CARD=vc4hdmi0 src/assets/boot.wav`. Si funciona, agregar
  `export RETRO_CONSOLE_AUDIO=plughw:CARD=vc4hdmi0` a `~/.xinitrc` antes de iniciar el programa.
- **No aparecen juegos:** comprobar las extensiones `.nes`, `.smc`, `.sfc` o `.gba`.
- **No abre el juego o no responde el control:** revisar `~/retro-console/mednafen.log`. Debe
  listar el control con su ID; si no, comprobar `ls /dev/input/js0` y que `groups` incluya `input`.

## Estructura

```
autorun.sh             Instalación
doc/                   Guías técnicas
src/retro_console.py   Frontend
src/control.py         Gamepad
src/emulador.py        Proceso de Mednafen y mapeo del control
src/importador.py      Detección de USB y copia sin duplicados
src/pantalla_usb.py    Pantalla de importación
src/retro-console.service  Arranque automático
src/retro-terminal.sh  Terminal de mantenimiento
src/retro-usb.sh       Montaje de USB en solo lectura
src/splash.py          Splash de arranque
src/assets/            Imagen y sonido de arranque
src/icons/             Íconos
src/tools/             Utilidades de desarrollo
src/THIRD_PARTY.md     Fuentes externas y licencias
vid/                   Enlace al video
```

## Licencia

El código propio usa licencia [MIT](LICENSE). Mednafen y las ROMs conservan sus propias
licencias.
