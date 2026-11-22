# Fuentes de ROMs legales (dominio público y homebrew)

## Propósito

Este documento recopila fuentes legítimas para obtener ROMs que pueden utilizarse en el
prototipo sin incurrir en infracción de derechos de autor. El proyecto requiere al menos
cinco ROMs precargadas; bajo ninguna circunstancia deben emplearse ROMs de juegos
comerciales con copyright vigente (por ejemplo, títulos originales de Nintendo, Capcom,
Konami, etc.), ya que su distribución o inclusión en un repositorio público constituye
una violación de derechos de autor y está explícitamente prohibida por la especificación
del curso.

## Categorías aceptables

- **Homebrew**: juegos desarrollados de manera independiente, específicamente para ser
  distribuidos de forma libre o gratuita por sus propios autores.
- **Dominio público**: obras cuyo periodo de protección de derechos de autor ha expirado,
  o que el titular de los derechos ha liberado explícitamente.
- **Freeware con licencia explícita**: software cuyo autor declara abiertamente que puede
  descargarse, usarse y, en algunos casos, redistribuirse sin costo.

En todos los casos, antes de utilizar un archivo descargado, debe verificarse la licencia
declarada por el autor en la propia fuente de descarga. Las etiquetas "gratis" y "dominio
público" no son equivalentes: un archivo puede ofrecerse sin costo y, aun así, no estar
legalmente disponible para redistribución.

## Fuentes sugeridas

- **[itch.io – colección de homebrew para SNES](https://itch.io/c/4842778/snes-homebrews)**
  y **[itch.io – juegos gratuitos etiquetados SNES](https://itch.io/games/free/tag-16-bit/tag-snes)**:
  plataforma donde desarrolladores independientes publican juegos homebrew para consolas
  retro, incluyendo archivos `.smc`/`.sfc` listos para usarse en un emulador. Cada página
  de juego indica explícitamente la licencia y el precio (gratuito, en los casos de
  interés para este proyecto).

- **[FreeROMs – ROMs de dominio público para SNES](https://www.freeroms.com/roms/snes/public_domain.htm)**:
  sección dedicada específicamente a ROMs catalogadas como de dominio público para Super
  Nintendo.

- **[STARESBACK.GG – ROMs legales](https://staresback.gg/legal-roms)**:
  catálogo que únicamente incluye ROMs homebrew cuyos autores han declarado explícitamente
  su libre distribución.

- **PDRoms**: proyecto de larga trayectoria dedicado a catalogar lanzamientos homebrew,
  donationware, de código abierto y de dominio público para múltiples sistemas retro,
  incluyendo SNES, NES y Game Boy Advance.

## Recomendaciones de uso para este proyecto

1. Descargar únicamente archivos cuya página de origen indique de forma explícita que son
   homebrew o de dominio público.
2. Conservar, dentro de `src/THIRD_PARTY.md`, el nombre del autor, la fuente de origen y la
   licencia de cada ROM utilizada, de la misma manera en que se documenta el código de
   terceros.
3. Verificar que las ROMs seleccionadas cubran distintos anchos de palabra (8, 16 y 32
   bits) cuando sea posible, conforme al componente clave de la especificación del curso.
4. Colocar los archivos finales en `~/retro-console/roms` en la Raspberry Pi, según lo
   descrito en `src/README.md`.
