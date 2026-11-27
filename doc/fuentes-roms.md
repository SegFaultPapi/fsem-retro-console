# Fuentes de ROMs legales

Autores: Rodríguez Montes de Oca Andrés, Vázquez Martínez Gustavo, Sánchez Álvarez Ángel Rubén · Licencia: MIT

## Propósito

La consola necesita al menos cinco ROMs precargadas, que cubran 8, 16 y 32 bits (NES, SNES y
Game Boy Advance). Este documento explica qué ROMs se pueden usar sin infringir derechos de autor
y dónde conseguirlas.

No se deben usar ROMs de juegos comerciales con derechos vigentes (por ejemplo, títulos
originales de Nintendo, Capcom o Konami). Distribuirlas o subirlas a un repositorio público es
una violación de derechos de autor y la especificación del curso lo prohíbe.

## Qué ROMs se aceptan

- **Homebrew:** juegos hechos de forma independiente para consolas retro, publicados por sus
  propios autores.
- **Dominio público:** obras cuyos derechos expiraron o que su titular liberó de forma explícita.
- **Freeware con licencia explícita:** juegos cuyo autor declara que se pueden descargar y usar
  sin costo y, a veces, redistribuir.

Antes de usar un archivo hay que revisar la licencia en su página de origen. «Gratis» no
significa «dominio público»: un juego puede descargarse sin costo y aun así no permitir que otros
lo redistribuyan.

Las ROMs no se guardan en el repositorio para mantener el entregable por debajo de 15 MB; cada una
se descarga de su fuente original.

## Fuentes utilizadas

Las ROMs de las memorias USB con las que se prueba la importación vienen de
[retrobrews/snes-games](https://github.com/retrobrews/snes-games), igual que siete de los juegos de
la galería. Autores, licencias y restricciones:
[`src/THIRD_PARTY.md`](../src/THIRD_PARTY.md).

Todo el catálogo de retrobrews/snes-games es de SNES (16 bits). Para cubrir los 8 y 32 bits del
componente clave se agregaron cuatro homebrew de código abierto publicados en GitHub: openNES
Snake y Thwaite (NES), y Notebook Adventure y Beat Beast (GBA). Se eligieron porque su licencia
permite redistribuirlos y porque cada autor publica el archivo listo para descargar.

## Otras fuentes

| Fuente | Sistemas | Notas |
|---|---|---|
| [itch.io: colección de homebrew para SNES](https://itch.io/c/4842778/snes-homebrews) | SNES | Cada página indica el precio y la licencia del juego |
| [itch.io: juegos gratuitos de SNES](https://itch.io/games/free/tag-16-bit/tag-snes) | SNES | Igual que la anterior |
| [FreeROMs: dominio público de SNES](https://www.freeroms.com/roms/snes/public_domain.htm) | SNES | Sección dedicada a ROMs de dominio público |
| [STARESBACK.GG: ROMs legales](https://staresback.gg/legal-roms) | Varios | Solo incluye homebrew que sus autores permiten distribuir |
| [PDRoms](https://pdroms.de) | NES, SNES, GBA y otros | Catálogo de homebrew, donationware, código abierto y dominio público |
| Proyectos de GitHub con licencia libre | NES, GBA y otros | Muchos juegos de *game jams* publican el ROM en sus *releases* |

## Recomendaciones

1. Descargar solo archivos cuya página de origen diga explícitamente que son homebrew, de dominio
   público o de libre distribución.
2. Registrar en `src/THIRD_PARTY.md` el título, el autor, la fuente y la licencia de cada ROM, igual
   que con el código de terceros.
3. Elegir ROMs de NES, SNES y GBA, para cubrir 8, 16 y 32 bits.
4. Copiar los archivos a `~/retro-console/roms` en la Raspberry Pi, como indica
   [`readme.MD`](../readme.MD).
