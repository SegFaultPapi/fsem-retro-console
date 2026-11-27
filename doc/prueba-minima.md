# Guía de pruebas

Autores: Rodríguez Montes de Oca Andrés, Vázquez Martínez Gustavo, Sánchez Álvarez Ángel Rubén · Licencia: MIT

Lista de comprobación para la consola ya instalada en la Raspberry Pi. Todas las pruebas se hacen
**sin teclado ni mouse**, solo con el gamepad.

## Preparación

1. Instalar según [`readme.MD`](../readme.MD) y reiniciar.
2. Colocar al menos 5 ROMs en `~/retro-console/roms`, con juegos de NES, SNES y GBA (ver
   [`fuentes-roms.md`](fuentes-roms.md)).
3. Conectar el control de Xbox One por USB, la pantalla y la salida de audio.
4. Preparar una memoria USB con una ROM nueva y una copia, con otro nombre, de una ROM que ya
   esté en la consola.

## Pruebas

| # | Acción | Resultado esperado |
|---|---|---|
| 1 | Encender | No aparecen mensajes de Linux ni el inicio de sesión |
| 2 | Esperar | Splash de 5 segundos con sonido y después la galería |
| 3 | Mover la cruceta | Cambia el título seleccionado |
| 4 | Abrir con A un juego de NES, uno de SNES y uno de GBA | Cada juego se ve, se escucha y responde al control |
| 5 | Presionar VIEW + MENU durante el juego | Regresa a la galería |
| 6 | Insertar la USB con un juego abierto | El juego se pausa y aparece la lista de importación |
| 7 | Revisar la lista | Una ROM importada y una duplicada |
| 8 | Elegir Continuar juego | Regresan la imagen, el sonido y el control del juego |
| 9 | Insertar la USB otra vez | Todas las ROMs aparecen como duplicadas |
| 10 | Elegir Volver a los títulos | Regresa a la galería, que ya incluye la ROM nueva |
| 11 | Desconectar y reconectar el control | El control se detecta de nuevo |
| 12 | Mantener VIEW + MENU 5 segundos en la galería | Aparece la terminal de mantenimiento; la misma combinación regresa |
| 13 | Elegir Reiniciar y presionar A dos veces | La consola vuelve sola a la galería |
| 14 | Elegir Apagar y presionar A dos veces | La Raspberry Pi se apaga |

Si algo falla, ver [`solucion-problemas.md`](solucion-problemas.md).

## Pruebas con teclado (solo desarrollo)

Con la sesión automática deshabilitada, `RETRO_CONSOLE_DEV=1 startx` permite navegar con las
flechas, Enter y Esc. Este modo no se usa en la consola final.
