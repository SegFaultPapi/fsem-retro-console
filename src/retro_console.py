#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Descripción: frontend de la consola: galería de títulos, navegación con
#              gamepad, estados de la partida e importación desde USB.
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

import tkinter as tk
from tkinter import PhotoImage
import os
import logging
import math
import queue
import subprocess as sp
import time
import sys
from PIL import Image, ImageTk
from control import Control
from pantalla_usb import PantallaUSB
from emulador import Emulador, es_rom, sistema_de, ultimo_mensaje
import importador
from splash import mostrar_splash

# Directorio donde se almacenan y buscan las ROMs (en la Raspberry Pi).
# Las portadas de cada juego también viven aquí, con el mismo nombre base
# que la ROM (p. ej. blt.sfc + blt.png).
directorio_actual = os.path.expanduser("~/retro-console/roms")
directorio = directorio_actual

# Directorio de los iconos de la interfaz
directorio_iconos = os.path.expanduser("~/retro-console/icons")

os.makedirs(directorio_actual, exist_ok=True)
os.makedirs(directorio_iconos, exist_ok=True)

logging.basicConfig(
    filename=os.path.expanduser("~/retro-console/consola.log"), filemode="w",
    level=logging.INFO, format="%(asctime)s %(message)s",
)

# Respaldo con teclado para pruebas del equipo; no cambia lo que se ve en
# pantalla. La consola se opera únicamente con gamepad.
MODO_DEV = os.environ.get("RETRO_CONSOLE_DEV") == "1"

# Columnas del grid de mosaicos (estilo galería de juegos).
COLUMNAS_GRID = 4
ANCHO_TILE = 180
ALTO_PORTADA = 150


# Estados de la consola. Las acciones del control se interpretan según el
# estado; así, lo que se presiona durante una partida no mueve el menú.
#   splash -> menu <-> juego
#   menu/juego -> usb_copiando -> usb_menu -> menu/juego
#   menu <-> terminal (VIEW + MENU durante 5 s)
estado = ["splash"]
usb_pendientes = []  # memorias conectadas que aún no se importan
eventos = queue.Queue()
control = Control(eventos)
emulador = Emulador()

def iniciar_juego(nombre_archivo):
    try:
        emulador.iniciar(os.path.join(directorio, nombre_archivo), control.descripcion)
    except OSError as e:
        logging.error("no se pudo abrir el emulador: %s", e)
        mostrar_aviso(f"No se pudo abrir el emulador: {e}")
        return
    estado[0] = "juego"
    label_instrucciones.config(
        text=f"Cargando {formatear_nombre_rom(nombre_archivo)}...", fg=COLOR_ACENTO)

def mostrar_aviso(texto):
    label_instrucciones.config(text=texto, fg="#ff6b6b")

def actualizar_estado_control():
    if control.descripcion:
        texto, color = "Control conectado", COLOR_ACENTO
    else:
        texto, color = "Conecta un control", "#ff6b6b"
    punto_control.config(fg=color)
    label_control.config(text=texto)

SEGUNDOS_TERMINAL = 5
combo_desde = [None]  # momento en que se presionó VIEW + MENU
vt_consola = [None]   # terminal virtual donde se dibuja la consola

def vt_activa():
    """Número de la terminal virtual visible, o None si no se puede saber."""
    try:
        with open("/sys/class/tty/tty0/active") as f:
            return int(f.read().strip().replace("tty", ""))
    except (OSError, ValueError):
        return None

def ejecutar_terminal(*args):
    try:
        r = sp.run(["sudo", "-n", "/usr/local/sbin/retro-terminal", *args],
                   capture_output=True, text=True, timeout=5)
    except (OSError, sp.TimeoutExpired) as e:
        logging.error("retro-terminal: %s", e)
        return False
    if r.returncode != 0:
        logging.error("retro-terminal: %s", r.stderr.strip())
    return r.returncode == 0

def revisar_terminal():
    # Si se volvió con el teclado (Ctrl+Alt+F1), también se recupera el control.
    if estado[0] == "terminal" and vt_activa() == vt_consola[0]:
        estado[0] = "menu"
        restaurar_texto_instrucciones()

    if combo_desde[0] is None or estado[0] not in ("menu", "terminal"):
        return
    transcurrido = time.monotonic() - combo_desde[0]
    if transcurrido < SEGUNDOS_TERMINAL:
        if estado[0] == "menu" and transcurrido > 1:
            mostrar_aviso(f"Abriendo terminal en {math.ceil(SEGUNDOS_TERMINAL - transcurrido)}...")
        return
    combo_desde[0] = None  # hay que soltar y volver a presionar
    if estado[0] == "terminal":
        ejecutar_terminal("volver", str(vt_consola[0]))
        return
    accion_pendiente[0] = None
    vt_consola[0] = vt_activa()
    if vt_consola[0] is not None and ejecutar_terminal("abrir"):
        estado[0] = "terminal"
    else:
        mostrar_aviso("No se pudo abrir la terminal")

def atender_evento(accion):
    if accion == "salir_juego":
        combo_desde[0] = time.monotonic()
    elif accion in ("combo_suelto", "desconectado"):
        if combo_desde[0] is not None and estado[0] == "menu":
            restaurar_texto_instrucciones()
        combo_desde[0] = None

    if isinstance(accion, tuple):
        tipo, dato = accion
        if tipo == "usb_insertada":
            if dato not in usb_pendientes:
                usb_pendientes.append(dato)
        else:
            mostrar_resultado_usb(dato)
    elif accion in ("conectado", "desconectado"):
        actualizar_estado_control()
    elif estado[0] == "juego":
        if accion == "salir_juego":
            emulador.terminar()
    elif estado[0] == "terminal":
        pass  # la consola no está a la vista: no debe responder
    elif estado[0] == "usb_menu":
        pantalla_usb.atender(accion)
    elif accion == "arriba":
        mover_seleccion(-1, 0)
    elif accion == "abajo":
        mover_seleccion(1, 0)
    elif accion == "izquierda":
        mover_seleccion(0, -1)
    elif accion == "derecha":
        mover_seleccion(0, 1)
    elif accion == "a":
        confirmar_seleccion()
    elif accion == "b":
        cancelar()

def cancelar():
    if estado[0] != "menu":
        return
    accion_pendiente[0] = None
    restaurar_texto_instrucciones()

def mostrar_frontend():
    # matchbox muestra al frente la última ventana en aparecer: se vuelve a
    # mapear para quedar sobre el emulador en pausa.
    app.withdraw()
    app.deiconify()
    app.attributes("-fullscreen", True)
    app.lift()
    app.focus_force()

def iniciar_importacion():
    global pantalla_usb
    nodo = usb_pendientes.pop(0)
    if estado[0] == "juego":
        emulador.pausar()
        mostrar_frontend()
    accion_pendiente[0] = None
    restaurar_texto_instrucciones()
    estado[0] = "usb_copiando"
    if pantalla_usb is None:
        pantalla_usb = PantallaUSB(app, al_elegir_usb)
    pantalla_usb.copiando()
    importador.importar_en_hilo(nodo, directorio, eventos)

def mostrar_resultado_usb(resultado):
    actualizar_lista_archivos()
    estado[0] = "usb_menu"
    pantalla_usb.resultado(resultado, emulador.activo())

def al_elegir_usb(opcion):
    global pantalla_usb
    if usb_pendientes:
        # Se conectó otra memoria mientras tanto: se atiende antes de salir.
        # El juego, si lo hay, sigue en pausa.
        iniciar_importacion()
        return
    pantalla_usb.destruir()
    pantalla_usb = None
    if not emulador.activo():
        estado[0] = "menu"
        return
    estado[0] = "juego"
    if opcion == "continuar":
        # Oculta el frontend para que el juego quede al frente.
        app.withdraw()
        emulador.reanudar()
    else:
        label_instrucciones.config(text="Cerrando el juego...", fg=COLOR_ACENTO)
        emulador.terminar()

def ciclo():
    # Único punto donde la interfaz atiende al control y al emulador.
    try:
        # Se revisa primero: lo que quedó en cola durante la partida se
        # atiende en estado "juego" y se descarta.
        while True:
            atender_evento(eventos.get_nowait())
    except queue.Empty:
        pass
    if estado[0] == "juego":
        codigo = emulador.revisar()
        if codigo is not None:
            estado[0] = "menu"
            restaurar_texto_instrucciones()
            if codigo != 0:
                mostrar_aviso(f"El juego no pudo abrirse: {ultimo_mensaje() or codigo}")
            mostrar_frontend()
    revisar_terminal()
    if usb_pendientes and (estado[0] == "menu" or (estado[0] == "juego" and emulador.activo()
                                                   and not emulador.cerrando())):
        iniciar_importacion()
    app.after(20, ciclo)

def cargar_archivos():
    os.makedirs(directorio, exist_ok=True)
    return sorted([archivo for archivo in os.listdir(directorio) if es_rom(archivo)])

EXTENSIONES_PORTADA = ('.png', '.jpg', '.jpeg')

def formatear_nombre_rom(nombre_archivo):
    # Convierte "mi-juego_2.sfc" en "Mi Juego 2": quita la extensión y separa
    # palabras por "-"/"_", dejando en mayúsculas los acrónimos cortos.
    base = os.path.splitext(nombre_archivo)[0]
    palabras = base.replace('_', ' ').replace('-', ' ').split()
    formateadas = [p if (p.isupper() and len(p) <= 4) else p.capitalize() for p in palabras]
    return ' '.join(formateadas) if formateadas else base

def obtener_sistema(nombre_archivo):
    sistema = sistema_de(nombre_archivo)
    return sistema[0] if sistema else '???'

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
    os.system("sudo -n systemctl poweroff")

def reiniciar():
    os.system("sudo -n systemctl reboot")

def salir(event):
    app.destroy()
    sys.exit(0)


# --- Navegación (juegos en grid + Apagar/Reiniciar en su propia franja) ---
# Cada tile tiene una posición lógica (fila, columna) en "posiciones", en el
# mismo orden que "tiles". No depende de cómo se vean agrupados visualmente.

def indice_de_tile(tile):
    return tiles.index(tile)

def restaurar_texto_instrucciones():
    label_instrucciones.config(text=texto_instrucciones, fg=COLOR_TEXTO_TENUE)

def resaltar_seleccion():
    # La selección se marca con una barrita de acento de altura FIJA (nunca
    # cambia de grosor, solo de color) y el color del título. Antes se usaba
    # el borde del widget (highlightbackground), pero un borde que aparece y
    # desaparece junto a tarjetas muy pegadas entre sí se percibe como que
    # "se mueven", aunque el tamaño real no cambiara.
    for i, tile in enumerate(tiles):
        seleccionado = (i == indice_seleccionado[0])
        color = COLOR_ACENTO if seleccionado else COLOR_PANEL
        if hasattr(tile, "barra_seleccion"):
            tile.barra_seleccion.configure(bg=color)
        if hasattr(tile, "lbl_titulo"):
            tile.lbl_titulo.configure(fg=COLOR_ACENTO if seleccionado else COLOR_TEXTO)

# --- Animación de "pulso" en la barra de la tarjeta seleccionada ---
# Solo cambia un color cada cierto intervalo: no toca ningún tamaño, así
# que no puede reintroducir el temblor que ya se arregló.
# (COLOR_PANEL_RGB/COLOR_ACENTO_RGB se calculan más abajo, una vez que
# existen COLOR_PANEL/COLOR_ACENTO; esta función solo los usa en tiempo
# de ejecución, no al definirse.)
_fase_pulso = [0.0]

def _interpolar_color(c1, c2, t):
    return '#%02x%02x%02x' % tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def animar_pulso():
    _fase_pulso[0] = (_fase_pulso[0] + 0.18) % (2 * math.pi)
    intensidad = 0.55 + 0.45 * ((math.sin(_fase_pulso[0]) + 1) / 2)
    if tiles:
        tile_actual = tiles[indice_seleccionado[0]]
        if hasattr(tile_actual, "barra_seleccion"):
            tile_actual.barra_seleccion.configure(
                bg=_interpolar_color(COLOR_PANEL_RGB, COLOR_ACENTO_RGB, intensidad)
            )
    app.after(90, animar_pulso)

def indice_en_fila(fila, columna_objetivo):
    candidatos = [i for i, (f, _c) in enumerate(posiciones) if f == fila]
    if not candidatos:
        return None
    return min(candidatos, key=lambda i: abs(posiciones[i][1] - columna_objetivo))

def mover_seleccion(delta_fila, delta_columna):
    if estado[0] != "menu" or not tiles:
        return
    if accion_pendiente[0] is not None:
        accion_pendiente[0] = None
        restaurar_texto_instrucciones()

    fila, columna = posiciones[indice_seleccionado[0]]

    if delta_columna != 0:
        objetivo = columna + delta_columna
        candidato = indice_en_fila(fila, objetivo)
        if candidato is not None and posiciones[candidato][1] == objetivo:
            indice_seleccionado[0] = candidato
            resaltar_seleccion()
            return

    if delta_fila != 0:
        filas_disponibles = sorted(set(f for f, _c in posiciones))
        fila_actual_idx = filas_disponibles.index(fila)
        nueva_fila_idx = fila_actual_idx + delta_fila
        if 0 <= nueva_fila_idx < len(filas_disponibles):
            candidato = indice_en_fila(filas_disponibles[nueva_fila_idx], columna)
            if candidato is not None:
                indice_seleccionado[0] = candidato
                resaltar_seleccion()

def confirmar_seleccion():
    if estado[0] != "menu" or not tiles:
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
        iniciar_juego(tile.archivo_item)

def seleccionar_tile_por_click(tile):
    indice_seleccionado[0] = indice_de_tile(tile)
    accion_pendiente[0] = None
    restaurar_texto_instrucciones()
    resaltar_seleccion()
    confirmar_seleccion()

def dibujar_tarjeta_redondeada(canvas, ancho, alto, radio, color, ox=0, oy=0):
    # Esquinas redondeadas sobre un Canvas, combinando rectángulos y arcos.
    # El Canvas mide siempre lo mismo en píxeles sin importar si al final
    # se dibuja una imagen real o el texto del placeholder encima.
    # (ox, oy) desplaza todo el dibujo, para poder usarlo también como sombra.
    canvas.create_rectangle(ox + radio, oy, ox + ancho - radio, oy + alto, fill=color, outline=color)
    canvas.create_rectangle(ox, oy + radio, ox + ancho, oy + alto - radio, fill=color, outline=color)
    canvas.create_arc(ox, oy, ox + 2 * radio, oy + 2 * radio, start=90, extent=90, fill=color, outline=color)
    canvas.create_arc(ox + ancho - 2 * radio, oy, ox + ancho, oy + 2 * radio, start=0, extent=90, fill=color, outline=color)
    canvas.create_arc(ox, oy + alto - 2 * radio, ox + 2 * radio, oy + alto, start=180, extent=90, fill=color, outline=color)
    canvas.create_arc(ox + ancho - 2 * radio, oy + alto - 2 * radio, ox + ancho, oy + alto, start=270, extent=90, fill=color, outline=color)

MARGEN_SOMBRA = 6
COLOR_SOMBRA = "#05060a"

def crear_canvas_portada(parent, archivo):
    ancho_portada = ANCHO_TILE - 20 - MARGEN_SOMBRA
    alto_portada = ALTO_PORTADA - MARGEN_SOMBRA
    canvas = tk.Canvas(
        parent, width=ancho_portada + MARGEN_SOMBRA, height=alto_portada + MARGEN_SOMBRA,
        bg=COLOR_PANEL, highlightthickness=0,
    )

    # Sombra: una copia oscura desfasada detrás de la tarjeta, para dar
    # sensación de profundidad (se asoma por abajo/derecha).
    dibujar_tarjeta_redondeada(canvas, ancho_portada, alto_portada, 12, COLOR_SOMBRA, ox=MARGEN_SOMBRA, oy=MARGEN_SOMBRA)

    ruta_portada = buscar_portada(archivo)
    imagen_cargada = False
    if ruta_portada:
        try:
            imagen = Image.open(ruta_portada).convert("RGB").resize((ancho_portada, alto_portada))
            foto = ImageTk.PhotoImage(imagen)
            imagenes_referencia.append(foto)
            canvas.create_image(ancho_portada // 2, alto_portada // 2, image=foto)
            imagen_cargada = True
        except Exception as e:
            print(f"[!] No se pudo cargar la portada de {archivo}: {e}")

    if not imagen_cargada:
        dibujar_tarjeta_redondeada(canvas, ancho_portada, alto_portada, 14, COLOR_BARRA)
        canvas.create_text(
            ancho_portada // 2, alto_portada // 2, text=obtener_sistema(archivo),
            fill=COLOR_ACENTO, font=("DejaVu Sans", 16, "bold"),
        )

    return canvas

def crear_tile_juego(parent, archivo):
    tile = tk.Frame(
        parent, bg=COLOR_PANEL, width=ANCHO_TILE, height=ALTO_PORTADA + 74,
        highlightthickness=0,
    )
    tile.grid_propagate(False)
    tile.tipo_item = "rom"
    tile.archivo_item = archivo

    canvas_portada = crear_canvas_portada(tile, archivo)
    canvas_portada.pack(padx=10, pady=(10, 8))

    # Barrita de acento: SIEMPRE mide lo mismo (altura fija), solo cambia de
    # color al seleccionar. Es el indicador de selección en vez de un borde.
    tile.barra_seleccion = tk.Frame(tile, bg=COLOR_PANEL, height=4)
    tile.barra_seleccion.pack(fill="x", padx=18)

    tile.lbl_titulo = tk.Label(
        tile, text=formatear_nombre_rom(archivo), bg=COLOR_PANEL, fg=COLOR_TEXTO,
        font=("DejaVu Sans", 11, "bold"), wraplength=ANCHO_TILE - 16, justify="center",
    )
    tile.lbl_titulo.pack(padx=8, pady=(6, 8))

    for widget in (tile, *tile.winfo_children()):
        widget.bind("<Button-1>", lambda event, t=tile: seleccionar_tile_por_click(t))

    return tile

def crear_boton_accion(parent, accion, etiqueta, icono, color_texto):
    # Botón angosto tipo "pastilla" (icono + texto en horizontal), para que
    # Apagar/Reiniciar se lean como acciones del sistema y no como más
    # juegos de la galería.
    boton = tk.Frame(
        parent, bg=COLOR_PANEL, width=190, height=60,
        highlightthickness=0,
    )
    boton.grid_propagate(False)
    boton.tipo_item = "accion"
    boton.accion_item = accion

    contenido = tk.Frame(boton, bg=COLOR_PANEL)
    contenido.place(relx=0.5, rely=0.42, anchor="center")

    tk.Label(contenido, image=icono, bg=COLOR_PANEL).pack(side="left", padx=(0, 10))
    tk.Label(
        contenido, text=etiqueta, bg=COLOR_PANEL, fg=color_texto,
        font=("DejaVu Sans", 13, "bold"),
    ).pack(side="left")

    boton.barra_seleccion = tk.Frame(boton, bg=COLOR_PANEL, height=4)
    boton.barra_seleccion.place(relx=0.5, rely=1.0, anchor="s", relwidth=0.8, y=-4)

    for widget in (boton, contenido, *contenido.winfo_children()):
        widget.bind("<Button-1>", lambda event, t=boton: seleccionar_tile_por_click(t))

    return boton

def construir_grid():
    label_galeria.config(text=f"GALERÍA DE JUEGOS ({len(archivos_actuales)})")
    for widget in contenedor_grid.winfo_children():
        widget.destroy()
    for widget in contenedor_acciones.winfo_children():
        widget.destroy()
    imagenes_referencia.clear()
    tiles.clear()
    posiciones.clear()

    for i, archivo in enumerate(archivos_actuales):
        tile = crear_tile_juego(contenedor_grid, archivo)
        fila, columna = divmod(i, COLUMNAS_GRID)
        tile.grid(row=fila, column=columna, padx=18, pady=18, sticky="n")
        tiles.append(tile)
        posiciones.append((fila, columna))

    # Las acciones viven en su propia franja debajo de la galería, pero
    # ocupan la "fila" lógica siguiente para la navegación con el control.
    fila_acciones = (len(archivos_actuales) + COLUMNAS_GRID - 1) // COLUMNAS_GRID if archivos_actuales else 0

    boton_apagar = crear_boton_accion(contenedor_acciones, "apagar", "Apagar", icono_apagar, "#ff6b6b")
    boton_apagar.grid(row=0, column=0, padx=10, pady=10)
    tiles.append(boton_apagar)
    posiciones.append((fila_acciones, 0))

    boton_reiniciar = crear_boton_accion(contenedor_acciones, "reiniciar", "Reiniciar", icono_reiniciar, "#e8c35c")
    boton_reiniciar.grid(row=0, column=1, padx=10, pady=10)
    tiles.append(boton_reiniciar)
    posiciones.append((fila_acciones, 1))

    if indice_seleccionado[0] >= len(tiles):
        indice_seleccionado[0] = max(0, len(tiles) - 1)
    resaltar_seleccion()

def actualizar_lista_archivos():
    archivos_actuales.clear()
    archivos_actuales.extend(cargar_archivos())
    construir_grid()

pantalla_usb = None
archivos_actuales = []
tiles = []
posiciones = []
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

# Usados por la animación de pulso de la barra de selección (ver animar_pulso).
COLOR_PANEL_RGB = tuple(int(COLOR_PANEL[i:i + 2], 16) for i in (1, 3, 5))
COLOR_ACENTO_RGB = tuple(int(COLOR_ACENTO[i:i + 2], 16) for i in (1, 3, 5))

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

# Indicador de estado del control (ver actualizar_estado_control).
frame_estado_control = tk.Frame(barra_encabezado, bg=COLOR_BARRA)
frame_estado_control.pack(side="right", padx=24)

punto_control = tk.Label(frame_estado_control, text="●", bg=COLOR_BARRA, font=("DejaVu Sans", 14))
punto_control.pack(side="left")

label_control = tk.Label(
    frame_estado_control, bg=COLOR_BARRA, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 12), padx=8,
)
label_control.pack(side="left")
actualizar_estado_control()

# Línea de acento bajo el encabezado, para separar visualmente del cuerpo.
tk.Frame(app, bg=COLOR_ACENTO, height=2).pack(side="top", fill="x")

# --- Pie de página: instrucciones ---
tk.Frame(app, bg=COLOR_BARRA, height=1).pack(side="bottom", fill="x")
barra_pie = tk.Frame(app, bg=COLOR_BARRA, height=50)
barra_pie.pack(side="bottom", fill="x")

texto_instrucciones = "Cruceta  Navegar      A  Confirmar      B  Cancelar      VIEW + MENU  Salir del juego"

label_instrucciones = tk.Label(
    barra_pie, text=texto_instrucciones, bg=COLOR_BARRA, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 12), padx=24,
)
label_instrucciones.pack(side="left", pady=12)

# --- Cuerpo principal: galería de juegos + franja de acciones del sistema ---
cuerpo = tk.Frame(app, bg=COLOR_FONDO)
cuerpo.pack(side="top", fill="both", expand=True)

zona_galeria = tk.Frame(cuerpo, bg=COLOR_FONDO)
zona_galeria.pack(fill="both", expand=True)

label_galeria = tk.Label(
    zona_galeria, text="GALERÍA DE JUEGOS", bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 11, "bold"), anchor="w",
)
label_galeria.pack(fill="x", padx=24, pady=(18, 4))

# "expand=True" sin "fill" centra el contenido en el espacio disponible
# (horizontal y vertical), en vez de quedar pegado arriba a la izquierda.
contenedor_grid = tk.Frame(zona_galeria, bg=COLOR_FONDO)
contenedor_grid.pack(expand=True)

tk.Frame(cuerpo, bg=COLOR_BARRA, height=1).pack(fill="x", padx=24)

zona_acciones = tk.Frame(cuerpo, bg=COLOR_FONDO)
zona_acciones.pack(fill="x", pady=(10, 20))

tk.Label(
    zona_acciones, text="SISTEMA", bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
    font=("DejaVu Sans", 11, "bold"), anchor="w",
).pack(fill="x", padx=24, pady=(10, 4))

contenedor_acciones = tk.Frame(zona_acciones, bg=COLOR_FONDO)
contenedor_acciones.pack()

construir_grid()

# Sin gestor de ventanas, X no le asigna el foco de entrada a la ventana
# por sí solo: hay que pedirlo explícitamente, o el teclado no llega a nadie.
app.lift()
app.focus_force()

if MODO_DEV:
    # Navegación de respaldo con teclado, solo para pruebas sin control físico.
    app.bind("<Escape>", salir)
    app.bind("<Up>", lambda event: atender_evento("arriba"))
    app.bind("<Down>", lambda event: atender_evento("abajo"))
    app.bind("<Left>", lambda event: atender_evento("izquierda"))
    app.bind("<Right>", lambda event: atender_evento("derecha"))
    app.bind("<Return>", lambda event: atender_evento("a"))

try:
    importador.vigilar(eventos)
except Exception as e:
    print(f"[!] No se pudo iniciar la detección de USB: {e}")

control.start()
ciclo()

animar_pulso()

def al_terminar_splash():
    estado[0] = "menu"

# La galería ya está construida debajo; el splash la cubre 5 segundos.
mostrar_splash(app, al_terminar_splash)

app.mainloop()
