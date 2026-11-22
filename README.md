# fsem-retro-console
Implementación de emulación de videojuegos retro para Raspberry Pi 4.

## Instalación de dependencias
Para instalar los requerimientos y dependencias necesarias, es necesario ejecutar los siguientes comandos.

En esta sección se implementó un script que automatiza la instalación del driver y del emulador, por lo que a continuación se presentan las instrucciones para descargar el proyecto y ejecutar dicho script.
Finalmente, debido a la naturaleza de su configuración, las modificaciones en los servicios de acceso remoto deben realizarse de forma manual.

```bash
git clone <URL-del-repositorio>
cd fsem-retro-console
chmod +x autorun.sh
./autorun.sh
```

### Instalación del Snes9x

```bash
# Descarga del repositorio
wget https://github.com/snes9xgit/snes9x/archive/refs/tags/1.60.tar.gz
# Descomprimirlo
tar -xzf 1.60.tar.gz
# Entrar en la carpeta descomprimida
cd snes9x-1.60/gtk
# Uso del comando meson
meson build --buildtype=release --strip
# Ingresamos a la carpeta creada del resultado del comando anterior
cd build
# Compilacion con el comando ninja
ninja
# Resultado final,  tenemos el emulador compilado y funcionando
./snes9x-gtk
```

### Instalación de los módulos de Python

Además, es necesario instalar todos los módulos requeridos por el script de Python con el siguiente comando:

```bash
pip install -r requirements.txt
```


# Configuración en la Raspberry Pi para la detección del control

El programa (`src/retro_console.py`) lee los eventos del control directamente
con la librería `evdev`, sin depender de drivers adicionales como xboxdrv.

Primero hay que verificar que el sistema reconozca el control:

```bash
lsusb
```

Si no aparece con ese comando, podemos listar los dispositivos de entrada:

```bash
ls /dev/input/by-id/
```

Para confirmar qué códigos de botones y ejes manda el control (útil si es un
modelo distinto al usado durante el desarrollo), se puede usar:

```bash
evtest /dev/input/eventX
```

Si los códigos reportados no coinciden con los que espera `joystick_control()`
en `retro_console.py` (cruceta = 544/545, botón B = 305, THUMBL = 317), hay que
actualizarlos ahí según lo que muestre `evtest` para ese control.

## Directorios que espera el programa

Antes de ejecutar `retro_console.py`, deben existir estas rutas en la Raspberry Pi:

- `~/retro-console/roms` — ahí se colocan las ROMs `.smc`/`.sfc`. El programa la
  crea automáticamente si no existe, pero debe tener al menos una ROM para
  poder probar la emulación.
- `~/retro-console/icons` — debe contener `apagadoScale.png`, `restartScale.png`
  e `instrucciones.png`, usados por la interfaz.
- `~/snes9x-1.60/gtk/build/snes9x-gtk` — el binario de Snes9x compilado según
  la sección anterior.

# Configuración de la Raspberry Pi para acceso remoto

Primero hay que configurarla como punto de acceso (AP) y servidor DHCP.
A continuación se detalla todo lo necesario:

```bash
sudo apt-get install dnsmasq hostapd
sudo pip3 install -U python-magic

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
```

Ahora nos dirigimos a /etc/dhcpcd.conf.

Creamos el archivo si es necesario.*
```bash
interface wlan0
static ip_address=192.168.28.254/24
nohook wpa_supplicant

sudo service dhcpcd restart
```

Ahora nos dirigimos a /etc/dnsmasq.conf:
```bash
\# Use the require wireless interface - usually wlan0
interface=wlan0
\# Reserve 20 IP addresses, set the subnet mask, and lease time
dhcp-range=192.168.28.200,192.168.28.220,255.255.255.0,24h

systemctl start dnsmasq
```

Ahora nos dirigimos a /etc/hostapd/hostapd.conf y agregamos lo siguiente:

```bash
# Wireless interface
interface=wlan0
# Specification: IEEE802.11
driver=nl80211
# The SSID or name of the network
ssid=retro-console
# Password of the network
wpa_passphrase=12345678
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
# Mode and frequency of operation
hw_mode=g
# Broadcast channel
channel=5
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
rsn_pairwise=CCMP
```

Ahora edite el archivo /etc/default/hostapd y reemplace la línea que comienza con #DAEMON\_CONF con:
DAEMON\_CONF="/etc/hostapd/hostapd.conf"

```bash
Ejecutamos killall wpa_supplicant
```

Y luego los siguientes:

```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
Verifique que los servicios se están ejecutando
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

Ahora es necesario activar SSH y el servidor VNC en la Raspberry.

En el cliente abrimos VNC Connect, ingresamos la IP de la Raspberry y
se nos pedirá el usuario y la contraseña.

Revisamos la resolución de la pantalla en:
Inicio > Preferencias > Raspberry Pi Configuration > Display

Configuramos la localización y la zona horaria en:
Inicio > Preferencias > Raspberry Pi Configuration > Localization

Reiniciamos la Raspberry Pi.

Para FileZilla, el cliente solo necesita la IP de la Raspberry,
el usuario, la contraseña y el puerto 22.

# Configuración para que la Raspberry tenga sonido al encender

Hay que colocar el archivo .wav en la carpeta soundboot.
Si no se tiene instalado, se instala con el siguiente comando:

```bash
sudo apt-get install alsa-utils
```

Ajustar el archivo .sh de acuerdo con la ruta en la que se encuentre.

Luego abrimos la terminal y ejecutamos lo siguiente:

```bash
sudo nano /etc/rc.local
```

Añadimos al final, antes de return 0;, la siguiente línea:

```bash
/usr/bin/aplay /home/<usuario>/Desktop/soundboot/jing.wav
```

Cerramos el archivo y reiniciamos.

# Ajuste de la imagen de inicio

La imagen debe ser PNG en tamaño 100x100 px.
Se puede escalar con ImageMagick; si no se tiene instalado, se hace con:

```bash
sudo apt-get install imagemagick
```

Para forzar el escalado, se usa el siguiente comando:

```bash
convert splash.png -resize 100x100\! splash2.png
```

Copiamos la carpeta pisplash; se recomienda mantener las imágenes dentro
de ese directorio. Nos colocamos dentro del directorio para poder
ejecutarlo, pero antes hay que cambiar los permisos.

```bash
chmod +x pisplash.sh
```

Para reemplazar la imagen, primero hay que revisar que la ruta sea la
correcta; en este caso se usa debian-theme, el cual tiene dos imágenes
relevantes: debian.png y logo.png.

El tema también debe configurarse en el siguiente archivo:
```bash
sudo nano  /etc/plymouth/plymouthd.conf
```

Con eso listo, nos colocamos en el directorio desde la terminal
y ejecutamos lo siguiente:

```bash
bash pisplash.sh /home/<usuario>/Desktop/pisplash/splash3.png
//bash pisplash.sh [img.png]
```

El initramfs se actualizará automáticamente; luego de eso, solo queda
reiniciar y listo.
