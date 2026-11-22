# Guía de prueba mínima en Raspberry Pi (modo teclado)

## Propósito

Este documento describe el procedimiento para desplegar y ejecutar una versión mínima
del prototipo sobre una Raspberry Pi con Raspbian Lite, utilizando el teclado como
método de control temporal mientras no se dispone de un gamepad físico para las
pruebas. Esta guía está dirigida a los integrantes del equipo y no constituye el
procedimiento de arranque final del proyecto.

## Requisitos físicos

- Raspberry Pi 4 con Raspbian Lite instalado.
- Pantalla con entrada HDMI y el cable correspondiente.
- Teclado conectado directamente a la Raspberry Pi. Esta prueba requiere acceso por
  consola local, ya que la interfaz debe renderizarse en la pantalla física conectada
  a la tarjeta; no es posible realizarla a través de una sesión SSH.
- Opcionalmente, una memoria USB con ROMs en formato `.smc`/`.sfc`, para validar el
  flujo de importación.

## Procedimiento

### 1. Clonar el repositorio

```bash
git clone https://github.com/SegFaultPapi/fsem-retro-console
cd fsem-retro-console
```

### 2. Ejecutar el script de instalación

```bash
chmod +x autorun.sh
./autorun.sh
```

Este script instala `python3-tk`, las dependencias de Python declaradas en
`requirements.txt`, y compila el emulador Snes9x en
`~/snes9x-1.60/gtk/build/snes9x-gtk`.

### 3. Instalar un servidor X mínimo

```bash
sudo apt-get install --no-install-recommends xserver-xorg xinit x11-xserver-utils
```

Esta instalación provee únicamente la capa gráfica necesaria para mostrar una ventana
en pantalla. No incluye ningún entorno de escritorio ni gestor de ventanas, por lo que
se mantiene conforme a la restricción del proyecto de no utilizar un entorno de
escritorio.

### 4. Agregar ROMs de prueba

El script `autorun.sh` ya crea `~/retro-console/roms` y `~/retro-console/icons`, y copia
automáticamente los íconos de la interfaz desde `src/icons/`. Solo falta colocar al menos
una ROM `.smc`/`.sfc` de prueba en `~/retro-console/roms/` (ver
[`doc/fuentes-roms.md`](fuentes-roms.md) para fuentes legales).

### 5. Configurar el inicio de la interfaz

Crear el archivo `~/.xinitrc`:

```bash
nano ~/.xinitrc
```

Con el siguiente contenido:

```bash
#!/bin/sh
export RETRO_CONSOLE_DEV=1
exec python3 ~/fsem-retro-console/src/retro_console.py
```

Otorgar permisos de ejecución:

```bash
chmod +x ~/.xinitrc
```

### 6. Ejecutar la aplicación

Desde la consola local de la Raspberry Pi (no por SSH):

```bash
startx
```

## Controles disponibles en este modo

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar la lista de ROMs disponibles |
| `Enter` | Ejecutar la ROM seleccionada en Snes9x |
| `Esc` | Cerrar la aplicación |

## Validaciones a realizar

- Confirmar que la interfaz se muestre a pantalla completa con la lista de ROMs
  cargada correctamente.
- Confirmar que la navegación y el lanzamiento de una ROM funcionen mediante el
  teclado.
- De manera opcional, insertar una memoria USB con ROMs y confirmar que los
  archivos se copien y se muestren en la ventana correspondiente.

## Alcance y limitaciones

Esta prueba tiene fines exclusivamente de validación durante el desarrollo. Las
siguientes limitaciones son intencionales y no deben interpretarse como fallas:

- La variable `RETRO_CONSOLE_DEV=1` habilita el control por teclado únicamente
  para pruebas. La versión final evaluada debe ejecutarse sin esta variable,
  exigiendo la presencia de un control físico.
- El arranque automático del sistema (systemd y autologin) aún no ha sido
  implementado; esta guía requiere iniciar la sesión y ejecutar `startx`
  manualmente.
- El flujo de importación por USB, en su estado actual, no pausa la emulación,
  no evita archivos duplicados ni solicita confirmación para continuar o volver
  al menú. Estas funciones se encuentran pendientes de implementación.
