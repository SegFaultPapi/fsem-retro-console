# Arquitectura

Autor: SegFaultPapi · Licencia: MIT

## Vista general

El sistema base es Raspberry Pi OS Lite, sin escritorio, paneles ni barras de título. Al
encender, la Raspberry Pi inicia sesión sola en `tty1` y arranca el entorno gráfico mínimo, que
solo contiene el frontend de la consola.

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

`matchbox-window-manager` no es un gestor de ventanas superpuestas: muestra una sola aplicación
a la vez, a pantalla completa y sin decoraciones. Se usa solo para que el frontend y Mednafen
reciban el foco y ocupen toda la pantalla.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `retro_console.py` | Galería, estados de la consola y ciclo principal |
| `control.py` | Traduce los eventos del gamepad en acciones y lo reconecta si se desenchufa |
| `emulador.py` | Inicia, pausa, reanuda y cierra Mednafen; genera el mapeo del control |
| `importador.py` | Detecta memorias USB, las monta y copia las ROMs sin duplicados |
| `pantalla_usb.py` | Capa de importación dentro de la ventana del frontend |
| `privilegios.py` | Ejecuta los pocos comandos que requieren permisos de root |
| `splash.py` | Imagen de 5 segundos con sonido |

Tkinter solo admite un hilo. Por eso los hilos del gamepad y de la importación no tocan la
interfaz: dejan mensajes en una cola que `ciclo()` revisa cada 20 ms.

## Estados

```
splash ──► menu ◄──► juego
            │ ▲        │ ▲
            ▼ │        ▼ │
       usb_copiando ─► usb_menu

menu ◄──► terminal        (VIEW + MENU durante 5 s)
```

Cada acción del control se interpreta según el estado actual. Durante una partida el menú no
responde, para que los botones del juego no abran otro título ni apaguen la consola.

## Control

Se usa un control de Xbox One con cable, que el kernel maneja con el controlador `xpad`. El
frontend lo lee con `evdev` sin tomarlo en exclusiva, porque Mednafen lee el mismo control por
`/dev/input/jsX`.

El mapeo de Mednafen se calcula cada vez que se abre un juego, así que no hay que configurar nada
a mano. El identificador del control se forma con el bus, el fabricante, el producto y la
versión (16 bits cada uno), el número de ejes, el número de botones y 32 bits en cero.

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

La consola se elige por la extensión de la ROM:

| Extensión | Consola | Bits | Módulo de Mednafen |
|---|---|---|---|
| `.nes` | NES | 8 | `nes` |
| `.smc`, `.sfc` | SNES | 16 | `snes_faust` |
| `.gba` | Game Boy Advance | 32 | `gba` |

- **Pausa:** `SIGSTOP` detiene el proceso con la partida en memoria y `SIGCONT` la reanuda.
- **Cierre:** `SIGTERM`, que Mednafen atiende de forma ordenada. Si no termina en 3 segundos, se
  fuerza el cierre.

## Importación desde USB

1. `pyudev` avisa que se conectó una memoria con sistema de archivos.
2. Si hay una partida abierta, se le envía `SIGSTOP` y el frontend pasa al frente.
3. `retro-usb` valida el dispositivo y lo monta con `ro,nosuid,nodev,noexec`.
4. Se recorren todas las carpetas y se calcula el SHA-256 de cada ROM.
5. Si ese contenido ya existe en la consola, la ROM se marca como duplicada aunque tenga otro
   nombre. En SNES se ignora el encabezado opcional de 512 bytes.
6. Cada ROM se copia con un nombre temporal y se renombra al terminar, para no dejar archivos a
   medias. Si el nombre ya lo usa otro juego, se guarda como `juego (2).nes`.
7. Se desmonta la memoria y se muestran las ROMs importadas, las duplicadas y los errores.
8. El usuario elige **Continuar juego** (`SIGCONT`) o **Volver a los títulos** (cierre ordenado).

## Arranque limpio

`src/arranque-limpio.sh` configura y verifica lo siguiente:

| Qué se oculta | Cómo |
|---|---|
| Arcoíris del firmware | `disable_splash=1` |
| Frambuesas y mensajes del kernel | `logo.nologo quiet loglevel=0 console=tty3` |
| Mensajes de systemd y udev | `systemd.show_status=false`, `udev.log_level=0` |
| Cursor | `vt.global_cursor_default=0` |
| Cualquier texto restante | `vt.default_red/grn/blu` en cero: texto negro sobre fondo negro |
| Inicio de sesión | `agetty --autologin` en `tty1` |

Si la consola falla en los primeros 10 segundos, la terminal recupera sus colores y muestra el
motivo. Los archivos originales se respaldan con la extensión `.retro-bak`.

## Permisos

El programa corre como usuario normal. Las reglas de `sudoers.d` solo permiten ejecutar sin
contraseña:

- `/usr/local/sbin/retro-usb`, para montar y desmontar memorias USB;
- `/usr/local/sbin/retro-terminal`, para cambiar a la terminal de mantenimiento;
- `systemctl poweroff` y `systemctl reboot`.

Los ayudantes pertenecen a root: el usuario puede ejecutarlos, pero no modificarlos.

## Archivos en la Raspberry Pi

| Ruta | Contenido |
|---|---|
| `~/retro-console/roms` | ROMs y portadas |
| `~/retro-console/mednafen` | Configuración de Mednafen y partidas guardadas |
| `~/retro-console/consola.log` | Registro del frontend y del control |
| `~/retro-console/mednafen.log` | Registro del último juego |
| `~/retro-console/startx.log` | Registro del servidor gráfico |
