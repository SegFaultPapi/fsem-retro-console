# Fuentes externas

Lista del software, el código consultado y las ROMs de terceros que usa la consola, con su
autor, licencia y origen. Fuentes consultadas el 24 de noviembre de 2026.

La licencia MIT de este repositorio cubre solo el código y los recursos propios; no cubre los
programas ni las ROMs listados aquí.

## Software utilizado

| Componente | Uso | Autor / proyecto | Licencia | Fuente |
|---|---|---|---|---|
| Mednafen | Emulador de NES, SNES y GBA | Equipo Mednafen y autores de cada núcleo | GPL-2.0 | https://mednafen.github.io |
| Python / Tkinter | Frontend | Python Software Foundation | PSF | https://docs.python.org/3/license.html |
| Pillow | Imágenes | Colaboradores de Pillow | HPND / MIT-CMU (según versión) | https://github.com/python-pillow/Pillow |
| python-evdev | Gamepad | Colaboradores de python-evdev | BSD-3-Clause | https://github.com/gvalkov/python-evdev |
| pyudev | Detección de USB | Colaboradores de pyudev | LGPL-2.1 o posterior | https://github.com/pyudev/pyudev |
| X.Org | Servidor gráfico | Fundación X.Org | MIT y similares | https://www.x.org |
| matchbox-window-manager | Enfoque y pantalla completa | Proyecto Matchbox | GPL-2.0 o posterior | https://git.yoctoproject.org/matchbox-window-manager |
| alsa-utils (`aplay`) | Sonido de arranque | Proyecto ALSA | GPL-2.0 | https://github.com/alsa-project/alsa-utils |

Son las licencias que declara cada proyecto. En la Raspberry Pi se pueden cotejar en
`/usr/share/doc/<paquete>/copyright`.

## Código fuente consultado

El formato del identificador del control y de la asignación de botones se obtuvo leyendo el
código fuente de Mednafen 1.32.1 (`Joystick_Linux.cpp` y `Joystick.cpp`), disponible en
https://mednafen.github.io/releases/. No se copió código.

## Recursos propios

Todo el código de `src/` y `autorun.sh` es propio, incluido `src/retro_console.py`. También son
propios:

- `src/assets/splash.png`, la imagen de arranque;
- `src/assets/boot.wav`, que se sintetiza con `src/tools/generar_sonido.py`, sin muestras externas;
- los íconos de `src/icons/` (`instrucciones.png`, `restartScale.png` y `apagadoScale.png`).

Todos usan la licencia MIT del repositorio.

## ROMs de retrobrews

Origen: https://github.com/retrobrews/snes-games (autores según su `README.md`; fechas y notas
según los `.txt` y `gamelist.xml` de cada juego).

> **Restricción:** retrobrews indica que las ROMs están aprobadas para distribución gratuita
> **solo en su sitio/proyecto** y pide contactar al autor para compartirlas. El repositorio no
> declara licencia general. Por eso **ninguna ROM se sube a este repositorio ni al `.7z`**;
> cada instalación las descarga de su origen.

**Uso en el proyecto:** las ROMs de las memorias USB con las que se prueba la importación
salieron de este catálogo. La tabla lo lista completo; la columna «En la consola» marca las que
aparecen en la galería final.

| En la consola | Archivo | Título | Autor(es) | Año | Licencia publicada |
|---|---|---|---|---|---|
|  | `astrohawk.smc` | Astrohawk | Paul Lay | 2003 | No encontrada |
| ✓ | `blt.sfc` | BLT | Charles Doty (cdoty) | 2012 | No encontrada |
|  | `bucket.smc` | Bucket | Sebastian Mihai | 2012 | No encontrada |
| ✓ | `furryrpg.sfc` | Furry RPG! | Ramsis | 2018 | Sin licencia formal; «open-source freeware» según [su autor](https://github.com/Ramsis-SNES/furryrpg) |
| ✓ | `hilda.sfc` | Hilda | Orochii Zouveleki (O_manko) | 2016 | No encontrada; [página](https://gamejolt.com/games/hilda/162284) |
| ✓ | `horizontal-shooter.sfc` | Horizontal Shooter | Marcus Rowe (Undisbeliever) | 2016 | Código MIT, imágenes CC0: [fuente](https://github.com/undisbeliever/horizontal-shooter) |
| ✓ | `jetpilotrising.sfc` | Jet Pilot Rising 1.1 | Dieter Von Laser (D4S) | 2008 o 2018 | No encontrada |
|  | `megafamilybros.smc` | Mega Family Bros | Debray Matthieu (Dieudunet) | 2012 | No encontrada |
|  | `nwarpdaisakusen.smc` | N-Warp Daisakusen 1.0 | Dieter Von Laser (D4S) | 2009 | No encontrada; «descarga gratuita» según su `.txt` |
| ✓ | `questformoney.sfc` | Uwol, Quest For Money | Alekmaul, Mojon Twins, KungfuFurby | 2012 | No encontrada |
|  | `rockfall.smc` | Rockfall | Paul Lay, Harvey A. Kong Tin | 1998 | No encontrada |
|  | `saf.smc` | Skipp And Friends: Unexpected Journey | Mukunda Johnson, Ken Snyder, Steven Velema, Hubert Lamontagne | 2009 | No encontrada |
| ✓ | `superbossgaiden.sfc` | Super Boss Gaiden 1.2 | Chrono Moogle, Dieter Von Laser (D4S) | 2016 | No encontrada |
|  | `tchouv2.smc` | Tchou 2 | Debray Matthieu (Dieudunet) | 2012 | No encontrada |

«No encontrada» no equivale a dominio público: los derechos siguen siendo del autor.

## ROMs homebrew de NES y GBA

Cubren los 8 y 32 bits del componente clave. Las cuatro tienen licencia que permite
redistribuirlas y se descargan de las *releases* de GitHub de cada autor.

| Archivo en la consola | Título | Sistema | Autor | Versión | Licencia | Descarga |
|---|---|---|---|---|---|---|
| `openNES-Snake.nes` | openNES Snake | NES (8 bits) | sebastiandine | v1.0.9 (2022) | zlib | https://github.com/sebastiandine/openNES-Snake/releases/download/v1.0.9/openNES-Snake-1.0.9.nes |
| `thwaite.nes` | Thwaite | NES (8 bits) | Damian Yerrick (pinobatch) | v0.04 (2018) | GPL-3.0 o posterior | https://github.com/pinobatch/thwaite-nes/releases/download/v0.04/thwaite.nes |
| `notebook-adventure.gba` | Notebook Adventure | GBA (32 bits) | NotImplementedLife | v1.3 (2022) | GPL-3.0 | https://github.com/NotImplementedLife/NotebookAdventure/releases/download/v1.3/NotebookAdventure-1-3.gba |
| `beat-beast.gba` | Beat Beast | GBA (32 bits) | afska | v1.1.7 (2024) | Código MIT; música CC BY-NC 4.0 y CC BY-NC-SA 3.0 (Synthenia); demás recursos según su carpeta `#licenses` | https://github.com/afska/beat-beast/releases/download/v1.1.7/BeatBeast_jam.gba |

Repositorios: [openNES-Snake](https://github.com/sebastiandine/openNES-Snake),
[thwaite-nes](https://github.com/pinobatch/thwaite-nes),
[NotebookAdventure](https://github.com/NotImplementedLife/NotebookAdventure) y
[beat-beast](https://github.com/afska/beat-beast).

Notas:

- Notebook Adventure se hizo para la Retro Platform Jam #4 y Beat Beast para la GBA Jam 2024.
- Beat Beast pesa unos 32 MB, el máximo de un cartucho de GBA; los recursos con licencia
  NonCommercial permiten este uso académico, pero no venderlo.
- Aunque las licencias lo permiten, estas ROMs tampoco se incluyen en el `.7z`, para respetar el
  límite de 15 MB.

## ROM de itch.io

| Archivo | Título | Autor | Versión | Precio | Licencia publicada | Página |
|---|---|---|---|---|---|---|
| `Rastan-SA1.sfc` | Rastan (SNES), edición SA-1 | EnriqueGGalvez (Enrique Gálvez) | Publicado en noviembre de 2026 | «Name your own price» | No encontrada | https://enriqueggalvez.itch.io/rastan-snes |

Es un port no oficial a SNES del juego de arcade *Rastan* de Taito (1987). La página no declara
licencia ni permiso de Taito, así que no se redistribuye: cada instalación lo descarga de su
página. La edición SA-1 requiere un emulador con soporte para ese coprocesador; también existe
una edición estándar (`Rastan.sfc`).

## ROMs comerciales

La galería final también incluye juegos comerciales de SNES:

| Título en la galería | Título | Desarrollador | Distribuidor | Año | Derechos |
|---|---|---|---|---|---|
| Contra III The Alien Wars (usa) | Contra III: The Alien Wars | Konami | Konami | 1992 | © Konami |
| Mortal Kombat (usa) (rev 1) | Mortal Kombat | Sculptured Software | Acclaim Entertainment | 1993 | © Midway; hoy de Warner Bros. Games |
| — | Mortal Kombat II | Sculptured Software | Acclaim Entertainment | 1994 | © Midway; hoy de Warner Bros. Games |
| Super Metroid (japan, USA) (en,ja) | Super Metroid | Nintendo R&D1 e Intelligent Systems | Nintendo | 1994 | © Nintendo |
| Super Mario World 2 Yoshi's Island (U) (v1.1) | Super Mario World 2: Yoshi's Island | Nintendo EAD | Nintendo | 1995 | © Nintendo |

Referencias de Mortal Kombat II: [MobyGames](https://www.mobygames.com/game/snes/mortal-kombat-ii)
y [The Cutting Room Floor](https://tcrf.net/Mortal_Kombat_II_(SNES)).

> **Restricción:** son juegos con derechos de autor vigentes y sin licencia de distribución.
> No se distribuyen con el proyecto: no se suben a este repositorio ni al `.7z`.
