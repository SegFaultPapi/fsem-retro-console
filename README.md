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

### Instalación de xboxdrv

```bash
sudo apt-get install \
 g++ \
 libboost-dev \
 scons \
 pkg-config \
 libusb-1.0-0-dev \
 git-core \
 libx11-dev \
 libudev-dev \
 x11proto-core-dev \
 libdbus-glib-1-dev
```

Ahora procedemos a descargar y compilar el driver.

```bash
# Descarga del repositorio oficial
git clone https://github.com/xboxdrv/xboxdrv.git
# Entramos en la carpeta del repositorio
cd xboxdrv
# Compilamos el proyecto
scons
# Instalamos este ejecutable en el sistema
make install
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

Primero hay que verificar que el sistema reconozca el control:

```bash
lsusb
```

Si aparece en la lista, podemos ejecutar xboxdrv estando dentro del
directorio correspondiente; si da error, intentar con sudo.

Si el control no aparece con ese comando, podemos ejecutar el siguiente:

```bash
ls /dev/input/by-id/
```

A partir de ahí identificamos nuestro control y copiamos el identificador que contenga 'event'.
Posteriormente lo reemplazamos en el siguiente comando:

```bash
sudo xboxdrv \
    --evdev /dev/input/by-id/<REEMPLAZAR> \
    --silent \
    --detach-kernel-driver \
    --deadzone 500 \
    --mimic-xpad \
    --evdev-absmap ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y \
    --evdev-keymap BTN_A=a,BTN_B=b,BTN_X=x,BTN_Y=y,BTN_TL=lb,BTN_TR=rb,BTN_THUMBL=tl,BTN_THUMBR=tr,BTN_MODE=guide,BTN_SELECT=back,BTN_START=start \
    --axismap -Y1=Y1,-Y2=Y2
```

Si funciona, el sistema indicará en qué event y js quedó disponible, pero
será necesario mantener el proceso abierto: si cerramos la terminal o
presionamos ctrl+c, es posible que se deshabilite. Para evitar esto,
creamos el siguiente script de inicio en init.d.

Primero creamos el archivo con:

```bash
sudo nano /etc/init.d/xboxdrv-startup
```

Ahora copiamos lo siguiente al archivo:

```bash
#!/bin/sh
### BEGIN INIT INFO
# Provides:          xboxdrv
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start xboxdrv on boot
### END INIT INFO

case "$1" in
    start)
        echo "Starting xboxdrv"
        /usr/local/bin/xboxdrv \
    	    --evdev /dev/input/by-id/<REEMPLAZAR> \
            --silent \
            --detach-kernel-driver \
            --deadzone 500 \
            --mimic-xpad \
            --evdev-absmap ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y \
            --evdev-keymap BTN_A=a,BTN_B=b,BTN_X=x,BTN_Y=y,BTN_TL=lb,BTN_TR=rb,BTN_THUMBL=tl,BTN_THUMBR=tr,BTN_MODE=guide,BTN_SELECT=back,BTN_START=start \
            --axismap -Y1=Y1,-Y2=Y2\
		&
        ;;
    stop)
        echo "Stopping xboxdrv"
        killall xboxdrv
        ;;
    *)
        echo "Usage: /etc/init.d/xboxdrv-startup {start|stop}"
        exit 1
        ;;
esac

exit 0
```

Verificamos dónde quedó instalado xboxdrv con el siguiente comando:

```bash
which xboxdrv
```

Copiamos la ruta y comprobamos que coincida con la que tenemos en el script;
si no coincide, la reemplazamos y asignamos permisos:

```bash
sudo chmod +x /usr/local/bin/xboxdrv
```

Si todo está bien entonces podremos iniciar el servicio con:

```bash
sudo /etc/init.d/xboxdrv-startup start
```

Para detenerlo basta con poner: 

```bash
sudo /etc/init.d/xboxdrv-startup stop
```

Para probar que funcione el mapeo entonces se hace con:

```bash
evtest /dev/input/event9
```

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
