# FSEm Retro Console

Consola de videojuegos retro para Raspberry Pi 4. Al encenderse muestra un splash propio con
sonido y abre una galería de títulos que se maneja solo con gamepad. Emula NES (8 bits), SNES
(16 bits) y Game Boy Advance (32 bits) con Mednafen, e importa ROMs desde una memoria USB.

Proyecto final de Fundamentos de Sistemas Embebidos. Todo el sistema parte de Raspberry Pi OS
Lite: no usa RetroPie ni distribuciones similares, ni un entorno de escritorio.

- **Repositorio:** https://github.com/SegFaultPapi/fsem-retro-console
- **Video-evidencia:** _pendiente de publicar_ (el enlace también estará en [`vid/video.txt`](vid/video.txt))
- **Autor:** [SegFaultPapi](https://github.com/SegFaultPapi)

## Estado

| Función | Estado |
|---|---|
| Arranque directo, sin inicio de sesión ni mensajes de Linux | Probado en la Raspberry Pi |
| Splash de 5 s con sonido | Probado en la Raspberry Pi |
| Galería, salida del juego, apagado y reinicio | Probado en la Raspberry Pi |
| Control de Xbox One con cable | Probado en la Raspberry Pi |
| Emulación con sonido (Mednafen: NES, SNES y GBA) | Probado en la Raspberry Pi; falta registrar la prueba de cada sistema |
| Importación por USB: pausa, copia, lista, duplicados, continuar o volver | Probado en la Raspberry Pi |
| Control remoto: apuntador (selector en pantalla que se mueve con la cruceta) y teclado | Implementado |
| ROMs precargadas | Copiadas a mano: SNES (retrobrews, itch.io y comerciales), NES y GBA (homebrew); el instalador no las descarga; falta probar las de NES y GBA |

## Materiales

- Raspberry Pi 4 con su fuente de alimentación y una tarjeta microSD.
- Pantalla HDMI y bocina con cable auxiliar de 3.5 mm (o una pantalla con audio).
- Control de Xbox One con cable USB, o cualquier otro que Linux reconozca.
- Memoria USB para importar ROMs (opcional).
- Conexión a Internet durante la instalación.

## Descarga e instalación

En un Raspberry Pi OS Lite recién instalado, como usuario normal (el script pide `sudo` cuando
lo necesita):

```bash
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/SegFaultPapi/fsem-retro-console
cd fsem-retro-console
bash autorun.sh
sudo reboot
```

`autorun.sh` hace lo siguiente:

- instala las dependencias y Mednafen;
- crea `~/retro-console` con las carpetas de ROMs, íconos y splash;
- configura el entorno gráfico mínimo, la importación por USB y el arranque directo;
- **reemplaza `~/.xinitrc`**.

Al terminar debe mostrar nueve `[OK]` y `[+] Listo`. Funciona desde cualquier carpeta y se puede
repetir sin riesgo. Por ahora no instala ROMs (ver la siguiente sección). `requirements.txt` es
solo de referencia: las librerías se instalan con `apt`, no con `pip`.

## ROMs

El repositorio no incluye ROMs, porque sus autores no permiten redistribuirlas. Para cargarlas:

1. Descargar los juegos de su origen. Las fuentes y sus licencias están en
   [`src/THIRD_PARTY.md`](src/THIRD_PARTY.md) y los criterios para elegirlos, en
   [`doc/fuentes-roms.md`](doc/fuentes-roms.md).
2. Copiar los archivos `.nes`, `.smc`, `.sfc` o `.gba` a `~/retro-console/roms`.
3. Opcional: agregar una portada con el mismo nombre base (por ejemplo, `blt.sfc` y `blt.png`).

Los homebrew de NES y GBA se pueden descargar directo en la Raspberry Pi:

```bash
cd ~/retro-console/roms
curl -fL -o openNES-Snake.nes https://github.com/sebastiandine/openNES-Snake/releases/download/v1.0.9/openNES-Snake-1.0.9.nes
curl -fL -o thwaite.nes https://github.com/pinobatch/thwaite-nes/releases/download/v0.04/thwaite.nes
curl -fL -o notebook-adventure.gba https://github.com/NotImplementedLife/NotebookAdventure/releases/download/v1.3/NotebookAdventure-1-3.gba
curl -fL -o beat-beast.gba https://github.com/afska/beat-beast/releases/download/v1.1.7/BeatBeast_jam.gba
```

## Uso

La consola inicia sola al encender. El splash dura 5 segundos y después aparece la galería.

| Acción | Gamepad | Teclado (solo desarrollo) |
|---|---|---|
| Navegar | Cruceta | Flechas |
| Confirmar | A | Enter |
| Cancelar o cerrar la lista de la USB | B | — |
| Salir del juego | VIEW + MENU | F12 (Mednafen) |
| Abrir la terminal o volver a la consola | VIEW + MENU durante 5 s en el menú | Ctrl+Alt+F2 / Ctrl+Alt+F1 |
| Cerrar el programa | — | Esc |

Dentro del juego, VIEW funciona como SELECT y MENU como START. En NES y GBA, A es A y X es B; en
SNES los botones corresponden por posición. El control se puede conectar después de encender.

Apagar y Reiniciar piden confirmación: hay que presionar A dos veces.

## Importar ROMs desde USB

1. Conectar la memoria (FAT32, exFAT, NTFS o ext) en la galería o durante una partida.
2. Si hay un juego abierto, se pausa. Las ROMs se copian aunque estén en subcarpetas; la memoria
   se monta en modo de solo lectura.
3. La pantalla muestra las ROMs importadas y las duplicadas. Una ROM es duplicada si su contenido
   (SHA-256) ya está en la consola, aunque tenga otro nombre.
4. Elegir **Continuar juego** o **Volver a los títulos** con la cruceta y A. A partir de ese
   momento la memoria se puede retirar.

## Mantenimiento

Al mantener VIEW + MENU durante 5 segundos en la galería aparece una terminal que pide usuario y
contraseña (para esto sí hace falta un teclado). La misma combinación regresa a la consola.

```bash
sudo systemctl restart getty@tty1       # reiniciar la consola
cat ~/retro-console/startx.log          # errores al iniciar el entorno gráfico
tail ~/retro-console/consola.log        # registro de la consola
```

Para probar con teclado, primero se vuelve al inicio de sesión normal (ver abajo) y luego se
ejecuta `RETRO_CONSOLE_DEV=1 startx` desde la consola local.

Para volver al inicio de sesión normal de Raspberry Pi OS:

```bash
sudo rm /etc/profile.d/retro-console.sh /etc/systemd/system/getty@tty1.service.d/zz-retro-console.conf
sudo cp /boot/firmware/cmdline.txt.retro-bak /boot/firmware/cmdline.txt
sudo reboot
```

## Splash y sonido

La imagen y el sonido por defecto están en `src/assets`. Para cambiarlos basta colocar
`splash.png` y `boot.wav` en `~/retro-console/splash`. El sonido original se genera con:

```bash
python3 src/tools/generar_sonido.py
```

## Documentación

| Documento | Contenido |
|---|---|
| [`doc/arquitectura.md`](doc/arquitectura.md) | Diseño, módulos, estados y arranque |
| [`doc/prueba-minima.md`](doc/prueba-minima.md) | Lista de pruebas en la Raspberry Pi |
| [`doc/solucion-problemas.md`](doc/solucion-problemas.md) | Problemas comunes y su solución |
| [`doc/fuentes-roms.md`](doc/fuentes-roms.md) | Dónde conseguir ROMs legales |
| [`src/THIRD_PARTY.md`](src/THIRD_PARTY.md) | Software y ROMs de terceros, con sus licencias |

## Estructura

```
autorun.sh               Instalador
doc/                     Documentación técnica
src/retro_console.py     Frontend: galería, estados y ciclo principal
src/control.py           Lectura del gamepad
src/emulador.py          Proceso de Mednafen y mapeo del control
src/importador.py        Detección de memorias USB y copia sin duplicados
src/pantalla_usb.py      Pantalla de importación
src/privilegios.py       Comandos que requieren permisos de root
src/splash.py            Splash de arranque
src/arranque-limpio.sh   Sesión automática y arranque sin mensajes
src/retro-autostart.sh   Inicio automático de la consola
src/retro-terminal.sh    Terminal de mantenimiento
src/retro-usb.sh         Montaje de memorias USB en solo lectura
src/assets/              Imagen y sonido de arranque
src/icons/               Íconos
src/tools/               Utilidades de desarrollo
src/THIRD_PARTY.md       Fuentes externas y licencias
vid/                     Enlace al video
```

## Licencia

El código y los recursos propios usan la licencia [MIT](LICENSE). Mednafen, las librerías y las
ROMs conservan sus propias licencias.
