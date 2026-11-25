# Solución de problemas

Autor: SegFaultPapi · Licencia: MIT

Para abrir una terminal, mantener **VIEW + MENU 5 segundos en el menú**. También se puede
entrar por SSH, si está habilitado.

## Problemas encontrados durante el desarrollo

### Sigue apareciendo el inicio de sesión y los mensajes de Linux

**Causa:** se descargó el código con `git pull`, pero no se ejecutó el instalador. `git pull`
solo copia archivos; la configuración del sistema la aplica `autorun.sh`.

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

**Solución:** localizarla con

```bash
find ~ -name autorun.sh
```

y entrar a la carpeta que lo contiene. `/usr/src` pertenece al sistema y no es la del proyecto.

### No funcionan Apagar, Reiniciar ni la terminal

**Causa:** no se instalaron las reglas de permisos porque `autorun.sh` no se ejecutó completo.

**Solución:** ejecutar `bash autorun.sh` y comprobar que existan `retro-console` y `retro-usb`:

```bash
sudo ls /etc/sudoers.d/
```

Apagar y Reiniciar requieren presionar A dos veces: la primera solo pide confirmación.

### El control mueve la selección, pero no abre el juego

**Causa:** Mednafen no estaba instalado. El registro mostraba la ruta `/usr/games/mednafen`.

**Solución:**

```bash
sudo apt-get update
sudo apt-get install -y mednafen
ls -l /usr/games/mednafen
```

### No se escucha nada por la bocina

**Causa:** el cable auxiliar.

**Solución:** probar primero la bocina y el cable con otro dispositivo, antes de cambiar la
configuración. Después comprobar la salida de la Raspberry Pi desde la carpeta del repositorio:

```bash
aplay -l
aplay src/assets/boot.wav
```

Si el cable funciona y el sonido sale por otro conector, agregar la salida correcta a
`~/.xinitrc`, antes de la línea que inicia el programa:

```bash
export RETRO_CONSOLE_AUDIO=plughw:CARD=Headphones   # o vc4hdmi0
```

`autorun.sh` regenera `~/.xinitrc`, por lo que hay que repetir este cambio después de
ejecutarlo.

## Otros problemas

| Síntoma | Qué revisar |
|---|---|
| «Conecta un control» | Cable USB, `lsusb` y `ls /dev/input/by-id/` |
| Los botones no corresponden | Los códigos registrados en `consola.log` y los de `src/control.py` |
| El control no responde dentro del juego | `ls /dev/input/js0` y que `groups` incluya `input` |
| Un juego no aparece | Extensión `.nes`, `.smc`, `.sfc` o `.gba`, y que no esté en una subcarpeta de `roms` |
| Un juego no abre | `file` sobre la ROM: si dice `HTML document`, se descargó la página y no el archivo |
| «No se pudo leer la memoria USB» | Formato FAT32, exFAT, NTFS o ext |
| Una ROM sale como duplicada | Su contenido ya está en la galería, quizá con otro nombre |
| Pantalla en negro más de un minuto | `startx.log`, por SSH |

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

Si la Raspberry Pi no arranca, la misma copia de `cmdline.txt` se puede hacer desde otra
computadora, en la partición de arranque de la microSD.
