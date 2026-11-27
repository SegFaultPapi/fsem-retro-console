# -*- coding: utf-8 -*-
#
# Descripción: pantalla de importación desde USB. Es una capa dentro de la
#              ventana del frontend, no una ventana aparte.
# Autor(es):   Rodríguez Montes de Oca Andrés (SegFaultPapi),
#              Vázquez Martínez Gustavo (snakeassasin6-cell),
#              Sánchez Álvarez Ángel Rubén (Baticonsola)
# Licencia:    MIT (ver LICENSE)

import tkinter as tk

FONDO, BARRA, TEXTO = "#12141c", "#232738", "#e7e9f0"
TENUE, ACENTO, ACENTO_TEXTO = "#8c91a8", "#3ddc97", "#0b1410"
LINEAS_VISIBLES = 9
FUENTE = "DejaVu Sans"


class PantallaUSB:
    def __init__(self, app, al_elegir):
        self.al_elegir = al_elegir
        self.capa = tk.Frame(app, bg=FONDO)
        self.capa.place(x=0, y=0, relwidth=1, relheight=1)
        self.capa.lift()

        self.titulo = tk.Label(self.capa, bg=FONDO, fg=ACENTO, font=(FUENTE, 24, "bold"))
        self.titulo.pack(pady=(36, 6))
        self.resumen = tk.Label(self.capa, bg=FONDO, fg=TEXTO, font=(FUENTE, 14))
        self.resumen.pack(pady=(0, 14))
        self.ayuda = tk.Label(self.capa, bg=BARRA, fg=TENUE, font=(FUENTE, 12), pady=12)
        self.ayuda.pack(side="bottom", fill="x")
        self.fila = tk.Frame(self.capa, bg=FONDO)
        self.fila.pack(side="bottom", pady=20)
        self.lista = tk.Label(
            self.capa, bg=FONDO, fg=TEXTO, font=(FUENTE, 13), justify="left", anchor="n")
        self.lista.pack(expand=True, fill="y")

        self.lineas, self.desplazamiento = [], 0
        self.opciones, self.botones, self.elegida = [], [], 0

    def copiando(self):
        self._limpiar_opciones()
        self.lineas, self.desplazamiento = [], 0
        self.titulo.config(text="Memoria USB detectada")
        self.resumen.config(text="Copiando ROMs, no retires la memoria...")
        self.ayuda.config(text="Espera un momento")
        self._dibujar_lista()

    def resultado(self, r, hay_juego):
        self._limpiar_opciones()
        self.titulo.config(text="Importación terminada")
        self.resumen.config(text=(
            f"Importadas: {len(r.nuevas)}     Duplicadas omitidas: {len(r.duplicadas)}"
            f"     Errores: {len(r.errores)}"))
        self.lineas = [f"+  {n}" for n in r.nuevas]
        self.lineas += [f"=  {n}  (ya existe)" for n in r.duplicadas]
        self.lineas += [f"!  {e}" for e in r.errores]
        if not self.lineas:
            self.lineas = ["La memoria no contiene ROMs compatibles."]
        self.desplazamiento = 0
        self._dibujar_lista()

        self.opciones = [("volver", "Volver a los títulos")]
        if hay_juego:
            self.opciones.insert(0, ("continuar", "Continuar juego"))
        for _clave, texto in self.opciones:
            boton = tk.Label(self.fila, text=texto, font=(FUENTE, 14, "bold"), padx=24, pady=12)
            boton.pack(side="left", padx=14)
            self.botones.append(boton)
        self._resaltar()
        ayuda = "A  Confirmar      Ya puedes retirar la memoria"
        if len(self.opciones) > 1:
            ayuda = "Izquierda / Derecha  Elegir      " + ayuda
        if len(self.lineas) > LINEAS_VISIBLES:
            ayuda = "Arriba / Abajo  Ver lista      " + ayuda
        self.ayuda.config(text=ayuda)

    def atender(self, accion):
        if accion in ("izquierda", "derecha"):
            paso = -1 if accion == "izquierda" else 1
            self.elegida = min(max(self.elegida + paso, 0), len(self.opciones) - 1)
            self._resaltar()
        elif accion in ("arriba", "abajo"):
            paso = -1 if accion == "arriba" else 1
            tope = max(0, len(self.lineas) - LINEAS_VISIBLES)
            self.desplazamiento = min(max(self.desplazamiento + paso, 0), tope)
            self._dibujar_lista()
        elif accion == "a":
            self.al_elegir(self.opciones[self.elegida][0])

    def destruir(self):
        self.capa.destroy()

    def _limpiar_opciones(self):
        for boton in self.botones:
            boton.destroy()
        self.opciones, self.botones, self.elegida = [], [], 0

    def _resaltar(self):
        for i, boton in enumerate(self.botones):
            activa = i == self.elegida
            boton.config(bg=ACENTO if activa else BARRA, fg=ACENTO_TEXTO if activa else TEXTO)

    def _dibujar_lista(self):
        fin = self.desplazamiento + LINEAS_VISIBLES
        visibles = [l if len(l) <= 60 else l[:57] + "..." for l in self.lineas[self.desplazamiento:fin]]
        if fin < len(self.lineas):
            visibles.append("...")
        self.lista.config(text="\n".join(visibles))
