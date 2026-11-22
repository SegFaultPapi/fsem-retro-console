#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import PhotoImage
import subprocess as sp
import time
import threading
import shutil
import os
import pyudev
from evdev import InputDevice, ecodes
import evdev
import sys
from PIL import Image, ImageTk

# Directorio donde se almacenan y buscan las ROMs (en la Raspberry Pi)
directorio_actual = os.path.expanduser("~/retro-console/roms")
directorio = directorio_actual
usb = 0
dispositivo = 0

# Directorio de los iconos de la interfaz y ruta del binario de Snes9x,
# instalados siguiendo las instrucciones de src/README.md
directorio_iconos = os.path.expanduser("~/retro-console/icons")
snes9x_bin = os.path.expanduser("~/snes9x-1.60/gtk/build/snes9x-gtk")

# Se crean aquí, antes de la detección del control, para que existan
# aunque el script termine por no encontrar un joystick.
os.makedirs(directorio_actual, exist_ok=True)
os.makedirs(directorio_iconos, exist_ok=True)

# Modo de desarrollo: permite probar con teclado cuando no hay un control
# conectado (p. ej. en WSL sin passthrough USB). NO se usa en la consola
# final, que debe operarse únicamente con gamepad.
MODO_DEV = os.environ.get("RETRO_CONSOLE_DEV") == "1"


# Busca el dispositivo de entrada del control
joystick = None

for device in [InputDevice(fn) for fn in evdev.list_devices()]:
    #capabilities = device.capabilities(verbose=True)
    if evdev.ecodes.EV_ABS in device.capabilities():
        joystick = device
        break

if joystick:
    print(f"Joystick detectado: {joystick.name}")
elif MODO_DEV:
    print("No se encontró un joystick. Modo de desarrollo activo: usando teclado (flechas + Enter).")
else:
    print("No se encontró un joystick.")
    sys.exit(1)


def ejecutar_snes9x(nombre_archivo):
    ruta_archivo = os.path.join(directorio, nombre_archivo)
    sp.run([snes9x_bin, ruta_archivo])

def cargar_archivos():
    os.makedirs(directorio, exist_ok=True)
    return sorted([archivo for archivo in os.listdir(directorio) if (archivo.endswith('.smc') or archivo.endswith('.sfc'))])

def on_tecla_arriba():
    selected_index = menu.curselection()
    if not selected_index:
        if menu.size() > 0:
            menu.selection_set(0)
        return
    new_index = max(0, selected_index[0] - 1)
    menu.selection_clear(0, tk.END)  # Limpiar la selección actual
    menu.selection_set(new_index)    # Establecer nueva selección
    menu.see(new_index)              # Hacer visible el nuevo ítem si está fuera de la vista

def on_tecla_abajo():
    selected_index = menu.curselection()
    if not selected_index:
        if menu.size() > 0:
            menu.selection_set(0)
        return
    new_index = min(menu.size() - 1, selected_index[0] + 1)
    menu.selection_clear(0, tk.END)
    menu.selection_set(new_index)
    menu.see(new_index)


def on_seleccion(event):
    widget = event.widget
    seleccionado = widget.get(widget.curselection())
    ejecutar_snes9x(seleccionado)


def on_clic_izquierdo():
    selected_index = menu.curselection()
    if selected_index:
        seleccionado = menu.get(selected_index[0])
        ejecutar_snes9x(seleccionado)

def apagar():
    os.system("shutdown now")

def reiniciar():
    os.system("reboot")

def salir(event):
    app.destroy()
    sys.exit(0)

def joystick_control():
    # Lee los eventos del control y navega el menú directamente,
    # sin simular movimientos de mouse ni teclado.
    for event in joystick.read_loop():
        if event.type == ecodes.EV_ABS and event.code == 17 and event.value != 0:
            # Cruceta vertical (eje Y)
            app.after(0, on_tecla_abajo if event.value == 1 else on_tecla_arriba)
        elif event.type == ecodes.EV_KEY and event.code == 545 and event.value == 1:
            # Cruceta abajo (como botón digital)
            app.after(0, on_tecla_abajo)
        elif event.type == ecodes.EV_KEY and event.code == 544 and event.value == 1:
            # Cruceta arriba (como botón digital)
            app.after(0, on_tecla_arriba)
        elif event.type == ecodes.EV_KEY and event.code == 305 and event.value == 1:
            # Botón B: confirma la selección y lanza la ROM
            app.after(0, on_clic_izquierdo)
        elif event.type == ecodes.EV_KEY and event.code == 317 and event.value == 1:
            # THUMBL: cierra la ventana de importación de USB, si hay una abierta
            app.after(0, cerrar_ventana_usb_activa)
        elif event.type == ecodes.EV_KEY and event.code == 307 and event.value == 1:
            print('Botón X presionado')
        elif event.type == ecodes.EV_KEY and event.code == 316 and event.value == 1:
            print('Botón XBOX presionado')


#Funciones necesarias para la detección de dispositivos USB

#Imprime las propiedades de un dispositivo
def print_dev_info(device):
    print("Device sys_path: {}".format(device.sys_path))
    print("Device sys_name: {}".format(device.sys_name))
    print("Device sys_number: {}".format(device.sys_number))
    print("Device subsystem: {}".format(device.subsystem))
    print("Device device_type: {}".format(device.device_type))
    print("Device is_initialized: {}".format(device.is_initialized))

#Obtiene el punto de montaje de un dispositivo USB
def get_mount_point(path):
    args = ["findmnt", "-unl", "-S", path]
    cp = sp.run(args, capture_output=True, text=True)
    out = cp.stdout.split(" ")[0]
    return out

#Manejador de eventos del Monitor-Observer: cambia una bandera al insertar o remover una USB
def check_dev_events(action, device):
    global usb
    global dispositivo
    if (action == "add"): #Si se inserta una USB
        usb = 1
        print_dev_info(device)
        dispositivo = device #Guarda el objeto dispositivo en la variable global
    if (action == "remove"): #Si se retira una USB
        usb = 0


def detectar_usb():
    global usb
    global dispositivo
    while True:
        time.sleep(4) #Espera para dar tiempo a que la USB termine de montarse
        if (usb == 1):
            time.sleep(4)
            usb_nuevo = get_mount_point("/dev/" + dispositivo.sys_name)
            print("La ruta del dispositivo es: " + usb_nuevo)
            mostrar_contenido_usb(usb_nuevo)
            usb = 0 #Reinicia la bandera de detección
        pass

        
def mostrar_contenido_usb(ruta_dispositivo):
    global dispositivo

    # Copia los archivos desde la USB al directorio local
    app.after(0, lambda: copiar_archivos_smc(ruta_dispositivo))
    
    #if dispositivo in ventanas:
    #    return
    
    print("La ruta del dispositivo es: " + ruta_dispositivo)
    archivos = [archivo for archivo in os.listdir(ruta_dispositivo) if (archivo.endswith('.smc') or archivo.endswith('.sfc'))]
    ventana_usb = tk.Toplevel()
    ventana_usb.overrideredirect(True)

    mensaje = f'Archivos en {dispositivo}:\n\n'
    mensaje += '\n'.join(archivos)

    etiqueta = tk.Label(ventana_usb, text=mensaje, justify='left', anchor='w')
    etiqueta.pack()

    ventanas[dispositivo] = ventana_usb

    ventana_usb.update_idletasks()
    ancho_ventana = ventana_usb.winfo_width()
    alto_ventana = ventana_usb.winfo_height()
    x_pantalla = (ventana_usb.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_pantalla = (ventana_usb.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana_usb.geometry('+{}+{}'.format(x_pantalla, y_pantalla))

    ventana_usb.mainloop()


def copiar_archivos_smc(desde_usb, a_directorio=directorio):
    try:
        if not os.path.exists(a_directorio):
            os.makedirs(a_directorio)

        archivos_smc = [archivo for archivo in os.listdir(desde_usb) if (archivo.endswith('.smc') or archivo.endswith('.sfc'))]

        for archivo in archivos_smc:
            origen = os.path.join(desde_usb, archivo)
            destino = os.path.join(a_directorio, archivo)
            shutil.copy(origen, destino)
            print(f"Archivo '{archivo}' copiado exitosamente.")
            
    except FileNotFoundError:
        print(f"Error: El directorio '{desde_usb}' no existe.")
    except Exception as e:
        print(f"Error al copiar archivos: {e}")

def actualizar_lista_archivos():
    menu.delete(0, tk.END)
    archivos = cargar_archivos()

    for archivo in archivos:
        menu.insert(tk.END, archivo)

def cerrar_ventana_usb_activa():
    # Cierra cualquier ventana de importación de USB que esté abierta
    for disp, ventana_usb in list(ventanas.items()):
        ventana_usb.destroy()
        ventanas.pop(disp, None)
    actualizar_lista_archivos()

ventanas = {}

archivos = cargar_archivos()

app = tk.Tk()
app.attributes("-fullscreen", True)

icono_apagar = PhotoImage(file=os.path.join(directorio_iconos, "apagadoScale.png"))
icono_reiniciar = PhotoImage(file=os.path.join(directorio_iconos, "restartScale.png"))

# Botón de apagar
btn_apagar = tk.Button(app, text="Apagar", command=apagar, bg="red", fg="white", image=icono_apagar, compound="right")
btn_apagar.pack(side=tk.RIGHT, padx=10, pady=10)

# Botón de reiniciar
btn_reiniciar = tk.Button(app, text="Reiniciar", command=reiniciar, bg="yellow", fg="black", image=icono_reiniciar, compound="right")
btn_reiniciar.pack(side=tk.RIGHT, padx=10, pady=10)


# Carga la imagen que se muestra debajo de los botones
imagen_debajo = Image.open(os.path.join(directorio_iconos, "instrucciones.png"))
imagen_debajo = ImageTk.PhotoImage(imagen_debajo)

# Coloca la imagen en la interfaz
label_imagen = tk.Label(app, image=imagen_debajo)
#label_imagen.pack(side=tk.RIGHT, anchor='sw')
label_imagen.place(relx=0.9, rely=0.95, anchor='s')

menu = tk.Listbox(app, selectbackground="lightblue", bg="white", fg="black", font=("Courier", 14))
menu.pack(side="left", fill="both", expand=True)

for archivo in archivos:
    menu.insert(tk.END, archivo)

menu.bind("<ButtonRelease-1>", on_seleccion)
app.bind("<Escape>", salir)

if MODO_DEV:
    # Navegación de respaldo con teclado, solo para pruebas sin control físico.
    app.bind("<Up>", lambda event: on_tecla_arriba())
    app.bind("<Down>", lambda event: on_tecla_abajo())
    app.bind("<Return>", lambda event: on_clic_izquierdo())

#Configura el Monitor-Observer para detectar cambios en los dispositivos de hardware
#En algunos entornos de prueba (p. ej. WSL sin soporte completo de netlink) esto
#puede no estar disponible; en ese caso se avisa y se continúa sin detección de USB.
try:
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="block", device_type="partition")
    observer = pyudev.MonitorObserver(monitor, check_dev_events, name='monitor-observer')
    observer.daemon = True #El MonitorObserver debe ser un hilo demonio
    observer.start()

    #Inicia un hilo para la detección de dispositivos USB
    hilo_usb = threading.Thread(target=detectar_usb)
    hilo_usb.daemon = True #Es importante que este hilo sea demonio
    hilo_usb.start()
except Exception as e:
    print(f"[!] No se pudo iniciar la detección de USB en este entorno: {e}")
    print("[!] El programa continúa sin la función de importación por USB.")

# Inicia un hilo para el control mediante el joystick, solo si hay uno conectado
if joystick:
    hilo_joystick = threading.Thread(target=joystick_control)
    hilo_joystick.daemon = True
    hilo_joystick.start()


app.mainloop()
