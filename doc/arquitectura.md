# Arquitectura

Autor: SegFaultPapi · Licencia: MIT

## Vista general

```
Encendido
  └─ getty@tty1 (sesión automática)
       └─ /etc/profile.d/retro-console.sh      (src/retro-autostart.sh)
            └─ startx → ~/.xinitrc
                 ├─ matchbox-window-manager    una aplicación a la vez, a pantalla completa
                 └─ retro_console.py           frontend
                      ├─ splash.py             imagen y sonido de arranque
                      ├─ control.py            hilo del gamepad
                      ├─ importador.py         detección y copia desde USB
                      │    └─ retro-usb        montaje en solo lectura
                      ├─ pantalla_usb.py       lista y opciones de la importación
                      └─ emulador.py
                           └─ mednafen         un proceso por partida
```

El sistema base es Raspberry Pi OS Lite. No hay escritorio, paneles ni barras de título.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `retro_console.py` | Galería, estados de la consola y ciclo principal |
| `control.py` | Traduce eventos del gamepad a acciones y lo reconecta si se desenchufa |
| `emulador.py` | Inicia, pausa, reanuda y cierra Mednafen; genera el mapeo del control |
| `importador.py` | Detecta memorias, las monta y copia las ROMs sin duplicados |
| `pantalla_usb.py` | Capa de importación dentro de la ventana del frontend |
| `privilegios.py` | Ejecuta los pocos comandos que requieren permisos de root |
| `splash.py` | Imagen de 5 segundos con sonido |

Los hilos del gamepad y de la importación no tocan la interfaz: dejan mensajes en una cola que
`ciclo()` atiende cada 20 ms. Así solo un hilo usa Tkinter.

## Estados

```
splash ──► menu ◄──► juego
            │ ▲        │ ▲
            ▼ │        ▼ │
       usb_copiando ─► usb_menu

menu ◄──► terminal        (VIEW + MENU durante 5 s)
```

Cada acción del control se interpreta según el estado. Durante una partida el menú no
responde, de modo que los botones del juego no abren otro título ni apagan la consola.

## Control

Se usa un control de Xbox One con cable, mediante el controlador `xpad` del kernel. El frontend
lo lee con `evdev` sin tomarlo en exclusiva, porque Mednafen lee el mismo control por
`/dev/input/jsX`.

El mapeo de Mednafen se calcula al abrir cada juego. El identificador del control se forma con
bus, fabricante, producto y versión (16 bits cada uno), número de ejes, número de botones y 32
bits en cero. Por eso no hay que configurar nada a mano.

| Control de Xbox | NES | SNES | GBA |
|---|---|---|---|
| A | A | B | A |
| B | — | A | — |
| X | B | Y | B |
| Y | — | X | — |
| LB / RB | — | L / R | L / R |
| VIEW / MENU | SELECT / START | SELECT / START | SELECT / START |
| Cruceta o stick izquierdo | Direcciones | Direcciones | Direcciones |

## Emulación

| Extensión | Consola | Bits | Módulo de Mednafen |
|---|---|---|---|
| `.nes` | NES | 8 | `nes` |
| `.smc`, `.sfc` | SNES | 16 | `snes_faust` |
| `.gba` | Game Boy Advance | 32 | `gba` |

- **Cierre:** `SIGTERM`, que Mednafen atiende de forma ordenada. Si no termina en 3 segundos se
  fuerza el cierre.
- **Pausa:** `SIGSTOP` detiene el proceso con la partida en memoria y `SIGCONT` la continúa.

## Importación desde USB

1. `pyudev` avisa que se conectó una memoria con sistema de archivos.
2. Si hay una partida, se envía `SIGSTOP` y el frontend pasa al frente.
3. `retro-usb` valida el dispositivo y lo monta con `ro,nosuid,nodev,noexec`.
4. Se recorren las carpetas y se calcula el SHA-256 de cada ROM.
5. Si el contenido ya existe, se marca como duplicado aunque el nombre sea distinto. En SNES se
   ignora el encabezado opcional de 512 bytes.
6. Se copia con nombre temporal y se renombra al terminar, para no dejar ROMs incompletas. Si
   el nombre ya lo usa otro juego, se guarda como `juego (2).nes`.
7. Se desmonta la memoria y se muestran las ROMs importadas, duplicadas y los errores.
8. Se elige **Continuar juego** (`SIGCONT`) o **Volver a los títulos** (cierre ordenado).

## Arranque limpio

`src/arranque-limpio.sh` configura y verifica lo siguiente:

| Qué se oculta | Cómo |
|---|---|
| Arcoíris del firmware | `disable_splash=1` |
| Frambuesas y mensajes del kernel | `logo.nologo quiet loglevel=0 console=tty3` |
| Mensajes de systemd y udev | `systemd.show_status=false`, `udev.log_level=0` |
| Cursor | `vt.global_cursor_default=0` |
| Cualquier texto restante | `vt.default_red/grn/blu` en cero: negro sobre negro |
| Inicio de sesión | `agetty --autologin` en tty1 |

Si la consola falla en los primeros 10 segundos, la terminal recupera sus colores y muestra el
motivo. Los archivos originales se conservan con extensión `.retro-bak`.

## Permisos

El programa corre como usuario normal. Las reglas de `sudoers.d` permiten sin contraseña solo:

- `/usr/local/sbin/retro-usb` (montar y desmontar memorias USB)
- `/usr/local/sbin/retro-terminal` (cambiar a la terminal de mantenimiento)
- `systemctl poweroff` y `systemctl reboot`

Los ayudantes pertenecen a root, por lo que el usuario puede ejecutarlos pero no modificarlos.

## Archivos en la Raspberry Pi

| Ruta | Contenido |
|---|---|
| `~/retro-console/roms` | ROMs y portadas |
| `~/retro-console/mednafen` | Configuración y partidas guardadas |
| `~/retro-console/consola.log` | Registro del frontend y del control |
| `~/retro-console/mednafen.log` | Registro del último juego |
| `~/retro-console/startx.log` | Registro del servidor gráfico |
