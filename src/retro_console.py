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

# Directorio donde se almacenan y buscan las ROMs (en la Raspberry Pi).
# Las portadas de cada juego también viven aquí, con el mismo nombre base
# que la ROM (p. ej. Rastan-SA1.sfc + Rastan-SA1.png).
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

# Columnas del grid de mosaicos (estilo galería de juegos).
COLUMNAS_GRID = 4
ANCHO_TILE = 180
ALTO_PORTADA = 150


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
    # Avisa que se está lanzando el juego: la interfaz se congela mientras
    # Snes9x corre (sp.run es bloqueante), así que sin esto parecería
    # que el programa no respondió al presionar la tecla/botón.
    texto_previo = label_instrucciones.cget("text")
    color_previo = label_instrucciones.cget("fg")
    label_instrucciones.config(text=f"Cargando {formatear_nombre_rom(nombre_archivo)}...", fg=COLOR_ACENTO)
    app.update_idletasks()
    try:
        sp.run([snes9x_bin, ruta_archivo])
    finally:
        label_instrucciones.config(text=texto_previo, fg=color_previo)

def cargar_archivos():
    os.makedirs(directorio, exist_ok=True)
    return sorted([archivo for archivo in os.listdir(directorio) if (archivo.endswith('.smc') or archivo.endswith('.sfc'))])

# Extensión de archivo -> nombre de consola que se muestra en cada mosaico.
SISTEMAS_POR_EXTENSION = {
    '.smc': 'SNES',
    '.sfc': 'SNES',
}

EXTENSIONES_PORTADA = ('.png', '.jpg', '.jpeg')

def formatear_nombre_rom(nombre_archivo):
    # Convierte "Rastan-SA1.sfc" en "Rastan SA1": quita la extensión y separa
    # palabras por "-"/"_", dejando en mayúsculas los acrónimos cortos.
    base = os.path.splitext(nombre_archivo)[0]
    palabras = base.replace('_', ' ').replace('-', ' ').split()
    formateadas = [p if (p.isupper() and len(p) <= 4) else p.capitalize() for p in palabras]
    return ' '.join(formateadas) if formateadas else base

def obtener_sistema(nombre_archivo):
    extension = os.path.splitext(nombre_archivo)[1].lower()
    return SISTEMAS_POR_EXTENSION.get(extension, '???')

def buscar_portada(nombre_archivo):
    # Busca una imagen con el mismo nombre base que la ROM, en el mismo
    # directorio, probando las extensiones de imagen más comunes.
    base = os.path.splitext(nombre_archivo)[0]
    for extension in EXTENSIONES_PORTADA:
        ruta = os.path.join(directorio, base + extension)
        if os.path.isfile(ruta):
            return ruta
    return None


def apagar():
    os.system("shutdown now")

def reiniciar():
    os.system("reboot")

def salir(event):
    app.destroy()
    sys.exit(0)


# --- Navegación del grid de mosaicos (juegos + Apagar + Reiniciar) ---

def indice_de_tile(tile):
    return tiles.index(tile)

def restaurar_texto_instrucciones():
    label_instrucciones.config(text=texto_instrucciones, fg=COLOR_TEXTO_TENUE)

def resaltar_seleccion():
    for i, tile in enumerate(tiles):
        if i == indice_seleccionado[0]:
            tile.configure(highlightthickness=4, highlightbackground=COLOR_ACENTO, highlightcolor=COLOR_ACENTO)
        else:
            tile.configure(highlightthickness=2, highlightbackground=COLOR_PANEL, highlightcolor=COLOR_PANEL)

def mover_seleccion(delta_fila, delta_columna):
    total = len(tiles)
    if total == 0:
        return
    if accion_pendiente[0] is not None:
        accion_pendiente[0] = None
        restaurar_texto_instrucciones()

    fila, columna = divmod(indice_seleccionado[0], COLUMNAS_GRID)

    if delta_columna != 0:
        nueva_columna = columna + delta_columna
        if 0 <= nueva_columna < COLUMNAS_GRID:
            candidato = fila * COLUMNAS_GRID + nueva_columna
            if candidato < total:
                indice_seleccionado[0] = candidato
                resaltar_seleccion()
                return

    if delta_fila != 0:
        nueva_fila = fila + delta_fila
        if nueva_fila >= 0:
            candidato = nueva_fila * COLUMNAS_GRID + columna
            if candidato < total:
                indice_seleccionado[0] = candidato
            else:
                ultimo_de_fila = min(total - 1, nueva_fila * COLUMNAS_GRID + COLUMNAS_GRID - 1)
                if nueva_fila * COLUMNAS_GRID < total:
                    indice_seleccionado[0] = ultimo_de_fila
            resaltar_seleccion()

def confirmar_seleccion():
    if not tiles:
        return
    tile = tiles[indice_seleccionado[0]]
    tipo = getattr(tile, "tipo_item", None)

    if tipo == "accion":
        accion = tile.accion_item
        if accion_pendiente[0] == accion:
            accion_pendiente[0] = None
            restaurar_texto_instrucciones()
            if accion == "apagar":
                apagar()
            else:
                reiniciar()
        else:
            accion_pendiente[0] = accion
            nombre = "apagar" if accion == "apagar" else "reiniciar"
            label_instrucciones.config(
                text=f"¿Confirmar {nombre}? Presiona de nuevo para confirmar, muévete para cancelar.",
                fg="#ff6b6b",
            )
    elif tipo == "rom":
        ejecutar_snes9x(tile.archivo_item)

def seleccionar_tile_por_click(tile):
    indice_seleccionado[0] = indice_de_tile(tile)
    accion_pendiente[0] = None
    restaurar_texto_instrucciones()
    resaltar_seleccion()
    confirmar_seleccion()

def joystick_control():
    # Lee los eventos del control y navega el grid directamente,
    # sin simular movimientos de mouse ni teclado.
    for event in joystick.read_loop():
        if event.type == ecodes.EV_ABS and event.code == 17 and event.value != 0:
            # Cruceta vertical (eje Y)
            app.after(0, lambda v=event.value: mover_seleccion(1 if v == 1 else -1, 0))
        elif event.type == ecodes.EV_ABS and event.code == 16 and event.value != 0:
            # Cruceta horizontal (eje X)
            app.after(0, lambda v=event.value: mover_seleccion(0, -1 if v == 1 else 1))
        elif event.type == ecodes.EV_KEY and event.code == 545 and event.value == 1:
            app.after(0, lambda: mover_seleccion(1, 0))
        elif event.type == ecodes.EV_KEY and event.code == 544 and event.value == 1:
            app.after(0, lambda: mover_seleccion(-1, 0))
        elif event.type == ecodes.EV_KEY and event.code == 546 and event.value == 1:
            app.after(0, lambda: mover_seleccion(0, -1))
        elif event.type == ecodes.EV_KEY and event.code == 547 and event.value == 1:
            app.after(0, lambda: mover_seleccion(0, 1))
        elif event.type == ecodes.EV_KEY and event.code == 305 and event.value == 1:
            # Botón B: confirma la selección actual (jugar / apagar / reiniciar)
            app.after(0, confirmar_seleccion)
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


def crear_tile_juego(parent, archivo):
    tile = tk.Frame(
        parent, bg=COLOR_PANEL, width=ANCHO_TILE, height=ALTO_PORTADA + 70,
        highlightthickness=2, highlightbackground=COLOR_PANEL,
    )
    tile.grid_propagate(False)
    tile.tipo_item = "rom"
    tile.archivo_item = archivo

    ruta_portada = buscar_portada(archivo)
    widget_portada = None
    if ruta_portada:
        try:
            imagen = Image.open(ruta_portada).resize((ANCHO_TILE - 20, ALTO_PORTADA))
            foto = ImageTk.PhotoImage(imagen)
            imagenes_referencia.append(foto)
            widget_portada = tk.Label(tile, image=foto, bg=COLOR_PANEL)
        except Exception as e:
            print(f"[!] No se pudo cargar la portada de {archivo}: {e}")

    if widget_portada is None:
        widget_portada = tk.Label(
            tile, text=obtener_sistema(archivo), bg=COLOR_BARRA, fg=COLOR_ACENTO,
            font=("DejaVu Sans", 16, "bold"), width=14, height=7,
        )

    widget_portada.pack(padx=10, pady=(10, 6))
    tk.Label(
        tile, text=formatear_nombre_rom(archivo), bg=COLOR_PANEL, fg=COLOR_TEXTO,
        font=("DejaVu Sans", 11, "bold"), wraplength=ANCHO_TILE - 16, justify="center",
    ).pack(padx=8, pady=(0, 8))

    for widget in (tile, *tile.winfo_children()):
        widget.bind("<Button-1>", lambda event, t=tile: seleccionar_tile_por_click(t))

    return tile

def crear_tile_accion(parent, accion, etiqueta, icono, color_texto):
    tile = tk.Frame(
        parent, bg=COLOR_PANEL, width=ANCHO_TILE, height=ALTO_PORTADA + 70,
        highlightthickness=2, highlightbackground=COLOR_PANEL,
    )
    tile.grid_propagate(False)
    tile.tipo_item = "accion"
    tile.accion_item = accion

    tk.Label(tile, image=icono, bg=COLOR_BARRA, width=ANCHO_TILE - 20, height=ALTO_PORTADA - 20).pack(padx=10, pady=(10, 6))
    tk.Label(
        tile, text=etiqueta, bg=COLOR_PANEL, fg=color_texto,
        font=("DejaVu Sans", 12, "bold"),
    ).pack(padx=8, pady=(0, 8))

    for widget in (tile, *tile.winfo_children()):
        widget.bind("<Button-1>", lambda event, t=tile: seleccionar_tile_por_click(t))

    return tile

def construir_grid():
    for widget in contenedor_grid.winfo_children():
        widget.destroy()
    imagenes_referencia.clear()
    tiles.clear()

    for i, archivo in enumerate(archivos_actuales):
        tile = crear_tile_juego(contenedor_grid, archivo)
        fila, columna = divmod(i, COLUMNAS_GRID)
        tile.grid(row=fila, column=columna, padx=14, pady=14, sticky="n")
        tiles.append(tile)

    base = len(archivos_actuales)
    tile_apagar = crear_tile_accion(contenedor_grid, "apagar", "Apagar", icono_apagar, "#ff6b6b")
    fila, columna = divmod(base, COLUMNAS_GRID)
    tile_apagar.grid(row=fila, column=columna, padx=14, pady=14, sticky="n")
    tiles.append(tile_apagar)

    tile_reiniciar = crear_tile_accion(contenedor_grid, "reiniciar", "Reiniciar", icono_reiniciar, "#e8c35c")
    fila, columna = divmod(base + 1, COLUMNAS_GRID)
    tile_reiniciar.grid(row=fila, column=columna, padx=14, pady=14, sticky="n")
    tiles.append(tile_reiniciar)

    if indice_seleccionado[0] >= len(tiles):
        indice_seleccionado[0] = max(0, len(tiles) - 1)
    resaltar_seleccion()

def actualizar_lista_archivos():
    archivos_actuales.clear()
    archivos_actuales.extend(cargar_archivos())
    construir_grid()

def cerrar_ventana_usb_activa():
    # Cierra cualquier ventana de importación de USB que esté abierta
    for disp, ventana_usb in list(ventanas.items()):
        ventana_usb.destroy()
        ventanas.pop(disp, None)
    actualizar_lista_archivos()

ventanas = {}
archivos_actuales = []
tiles = []
imagenes_referencia = []
indice_seleccionado = [0]
accion_pendiente = [None]

archivos_actuales.extend(cargar_archivos())

# Paleta de la interfaz: tema oscuro tipo consola, con un acento verde para
# selección/estado activo y rojo reservado solo para apagar.
COLOR_FONDO = "#12141c"
COLOR_PANEL = "#1b1e2b"
COLOR_BARRA = "#232738"
COLOR_TEXTO = "#e7e9f0"
COLOR_TEXTO_TENUE = "#8c91a8"
COLOR_ACENTO = "#3ddc97"
COLOR_ACENTO_TEXTO = "#0b1410"

app = tk.Tk()
# matchbox-window-manager (configurado en ~/.xinitrc) es quien maximiza y
# le da el foco de teclado a esta ventana. "overrideredirect" NO debe usarse
# aquí: le indica a cualquier gestor de ventanas que la ignore por completo,
# lo cual impide que reciba el foco correctamente.
app.attributes("-fullscreen", True)
app.configure(bg=COLOR_FONDO)

icono_apagar = PhotoImage(file=os.path.join(directorio_iconos, "apagadoScale.png"))
icono_reiniciar = PhotoImage(file=os.path.join(directorio_iconos, "restartScale.png"))

# --- Encabezado ---
barra_encabezado = tk.Frame(app, bg=COLOR_BARRA, height=70)
barra_encabezado.pack(side="top", fill="x")

tk.Label(
    barra_encabezado, text="FSEM RETRO CONSOLE", bg=COLOR_BARRA, fg=COLOR_ACENTO,
    font=("DejaVu Sans", 22, "bold"), padx=24,
).pack(side="left", pady=10)

# Indicador de estado del control: útil para saber de un vistazo si el
# sistema detectó el gamepad, sin tener que mirar la terminal.
if joystick:
    texto_estado_control = "Control conectado"
    color_estado_control = COLOR_ACENTO
elif MODO_DEV:
    texto_estado_control = "Modo teclado (dev)"
    color_estado_control = "#e8c35c"
else:
    texto_estado_control = "Sin control"
    color_estado_control = "#ff6b6b"

frame_estado_control = tk.Frame(barra_encabezado, bg=COLOR_BARRA)
frame_estado_control.pack(side="right", padx=24)

tk.Label(
    frame_estado_control, text="●", bg=COLOR_BARRA, fg=color_estado_control,
    font=("DejaVu Sans", 14),
).pack(side="left")

tk.Label(
    frame_estado_control, text=texto_estado_control, bg=COLOR_BARRA, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 12), padx=8,
).pack(side="left")

# Línea de acento bajo el encabezado, para separar visualmente del cuerpo.
tk.Frame(app, bg=COLOR_ACENTO, height=2).pack(side="top", fill="x")

# --- Pie de página: instrucciones ---
tk.Frame(app, bg=COLOR_BARRA, height=1).pack(side="bottom", fill="x")
barra_pie = tk.Frame(app, bg=COLOR_BARRA, height=50)
barra_pie.pack(side="bottom", fill="x")

if MODO_DEV:
    texto_instrucciones = "↑ ↓ ← →  Navegar      Enter  Confirmar      Esc  Salir"
else:
    texto_instrucciones = "Cruceta  Navegar      Botón B  Confirmar"

label_instrucciones = tk.Label(
    barra_pie, text=texto_instrucciones, bg=COLOR_BARRA, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 12), padx=24,
)
label_instrucciones.pack(side="left", pady=12)

# --- Cuerpo principal: grid de mosaicos (juegos + Apagar + Reiniciar) ---
cuerpo = tk.Frame(app, bg=COLOR_FONDO)
cuerpo.pack(side="top", fill="both", expand=True)

tk.Label(
    cuerpo, text="GALERÍA DE JUEGOS", bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 11, "bold"), anchor="w",
).pack(fill="x", padx=24, pady=(18, 4))

contenedor_grid = tk.Frame(cuerpo, bg=COLOR_FONDO)
contenedor_grid.pack(padx=10, pady=10)

construir_grid()

app.bind("<Escape>", salir)

# Sin gestor de ventanas, X no le asigna el foco de entrada a la ventana
# por sí solo: hay que pedirlo explícitamente, o el teclado no llega a nadie.
app.lift()
app.focus_force()

if MODO_DEV:
    # Navegación de respaldo con teclado, solo para pruebas sin control físico.
    app.bind("<Up>", lambda event: mover_seleccion(-1, 0))
    app.bind("<Down>", lambda event: mover_seleccion(1, 0))
    app.bind("<Left>", lambda event: mover_seleccion(0, -1))
    app.bind("<Right>", lambda event: mover_seleccion(0, 1))
    app.bind("<Return>", lambda event: confirmar_seleccion())

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
