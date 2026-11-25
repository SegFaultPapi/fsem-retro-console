# Guía de pruebas

Autor: SegFaultPapi · Licencia: MIT

Lista de comprobación de la consola instalada en la Raspberry Pi, **sin teclado ni mouse**.

## Preparación

1. Instalar según [`readme.MD`](../readme.MD) y reiniciar.
2. Colocar al menos 5 ROMs en `~/retro-console/roms`, con juegos de NES, SNES y GBA
   (ver [`fuentes-roms.md`](fuentes-roms.md)).
3. Conectar el control de Xbox One por USB, la pantalla y la salida de audio.
4. Preparar una memoria USB con una ROM nueva y otra repetida con nombre distinto.

## Pruebas

| # | Acción | Resultado esperado |
|---|---|---|
| 1 | Encender | Sin mensajes de Linux ni inicio de sesión |
| 2 | Esperar | Splash de 5 segundos con sonido y después la galería |
| 3 | Mover la cruceta | Cambia la selección |
| 4 | Abrir un juego de NES, uno de SNES y uno de GBA con A | Se ven, se escuchan y responden al control |
| 5 | VIEW + MENU durante el juego | Regresa a la galería |
| 6 | Insertar la USB con un juego abierto | El juego se pausa y aparece la lista |
| 7 | Revisar la lista | Una ROM importada y una duplicada |
| 8 | Elegir Continuar juego | Vuelven la imagen, el sonido y el control |
| 9 | Insertar la USB otra vez | Todo sale duplicado |
| 10 | Elegir Volver a los títulos | Regresa a la galería, con la ROM nueva |
| 11 | Desconectar y reconectar el control | Se detecta de nuevo |
| 12 | VIEW + MENU 5 segundos en el menú | Terminal de mantenimiento; la misma combinación regresa |
| 13 | Reiniciar, con A dos veces | La consola vuelve sola a la galería |
| 14 | Apagar, con A dos veces | La Raspberry Pi se apaga |

Si algo falla, ver [`solucion-problemas.md`](solucion-problemas.md).

## Pruebas con teclado (solo desarrollo)

`RETRO_CONSOLE_DEV=1 startx`, con la sesión automática deshabilitada, permite navegar con las
flechas, Enter y Esc. No se usa en la consola final.
