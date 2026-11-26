# Solución de problemas

Autor: SegFaultPapi · Licencia: MIT

Para abrir una terminal en la Raspberry Pi, mantener **VIEW + MENU durante 5 segundos en la
galería** (hace falta un teclado para iniciar sesión). También se puede entrar por SSH, si está
habilitado.

## Problemas encontrados durante el desarrollo

### Siguen apareciendo el inicio de sesión y los mensajes de Linux

**Causa:** se actualizó el código con `git pull`, pero no se volvió a ejecutar el instalador.
`git pull` solo descarga archivos; la configuración del sistema la aplica `autorun.sh`.

**Solución:**

```bash
cd ~/fsem-retro-console
git pull
bash autorun.sh
sudo reboot
```

Al final deben aparecer nueve `[OK]` y `[+] Listo`. Si aparece `[X]`, esa línea indica el paso
que falló.

### `No such file or directory` al ejecutar los scripts

**Causa:** el comando se ejecutó fuera de la carpeta del repositorio.

**Solución:** buscar la carpeta con

```bash
find ~ -name autorun.sh
```

y entrar a la que lo contiene. `/usr/src` es una carpeta del sistema, no la del proyecto.

### No funcionan Apagar, Reiniciar ni la terminal

**Causa:** no se instalaron las reglas de permisos porque `autorun.sh` no terminó.

**Solución:** ejecutar `bash autorun.sh` y comprobar que existan `retro-console` y `retro-usb`
con:

```bash
sudo ls /etc/sudoers.d/
```

Recordar que Apagar y Reiniciar requieren presionar A dos veces: la primera solo pide
confirmación.

### El control mueve la selección, pero no abre el juego

**Causa:** Mednafen no estaba instalado; el registro mostraba que faltaba
`/usr/games/mednafen`.

**Solución:**

```bash
sudo apt-get update
sudo apt-get install -y mednafen
ls -l /usr/games/mednafen
```

### No se escucha nada por la bocina

**Causa:** una falla del cable auxiliar, no de la Raspberry Pi.

**Solución:** probar la bocina y el cable con otro dispositivo antes de cambiar la configuración.
Después, desde la carpeta del repositorio, comprobar la salida de audio de la Raspberry Pi:

```bash
aplay -l
aplay src/assets/boot.wav
```

Si el cable funciona pero el sonido sale por otro conector, agregar la salida correcta en
`~/.xinitrc`, antes de la línea que inicia el programa:

```bash
export RETRO_CONSOLE_AUDIO=plughw:CARD=Headphones   # o vc4hdmi0 para HDMI
```

`autorun.sh` vuelve a generar `~/.xinitrc`, así que este cambio se debe repetir cada vez que se
ejecute el instalador.

## Otros problemas

| Síntoma | Qué revisar |
|---|---|
| Aparece «Conecta un control» | El cable USB, `lsusb` y `ls /dev/input/by-id/` |
| Los botones no corresponden | Los códigos que registra `consola.log` contra los de `src/control.py` |
| El control no responde dentro del juego | Que exista `/dev/input/js0` y que `groups` incluya `input` |
| Un juego no aparece en la galería | Que la extensión sea `.nes`, `.smc`, `.sfc` o `.gba` y que no esté en una subcarpeta de `roms` |
| Un juego no abre | `file <rom>`: si dice `HTML document`, se descargó la página web en lugar del archivo |
| «No se pudo leer la memoria USB» | Que el formato sea FAT32, exFAT, NTFS o ext |
| Una ROM aparece como duplicada | Su contenido ya está en la galería, posiblemente con otro nombre |
| Pantalla en negro por más de un minuto | `startx.log`, por SSH |

## Registros

```bash
tail -30 ~/retro-console/consola.log
tail -30 ~/retro-console/mednafen.log
tail -30 ~/retro-console/startx.log
```

## Revertir el arranque limpio

```bash
sudo rm /etc/profile.d/retro-console.sh /etc/systemd/system/getty@tty1.service.d/zz-retro-console.conf
sudo cp /boot/firmware/cmdline.txt.retro-bak /boot/firmware/cmdline.txt
sudo reboot
```

Si la Raspberry Pi ya no arranca, la misma copia de `cmdline.txt` se puede hacer desde otra
computadora, en la partición de arranque de la microSD.
