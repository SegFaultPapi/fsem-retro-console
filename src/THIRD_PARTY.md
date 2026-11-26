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
| ✓ | `jetpilotrising.sfc` | Jet Pilot Rising 1.1 | Dieter Von Laser (D4S) | 2008 o 2018 (1) | No encontrada |
|  | `megafamilybros.smc` | Mega Family Bros | Debray Matthieu (Dieudunet) | 2012 | No encontrada |
|  | `nwarpdaisakusen.smc` | N-Warp Daisakusen 1.0 | Dieter Von Laser (D4S) | 2009 | No encontrada; «descarga gratuita» según su `.txt` |
| ✓ | `questformoney.sfc` | Uwol, Quest For Money | Alekmaul, Mojon Twins, KungfuFurby | 2012 | No encontrada |
|  | `rockfall.smc` | Rockfall | Paul Lay, Harvey A. Kong Tin | 1998 | No encontrada (2) |
|  | `saf.smc` | Skipp And Friends: Unexpected Journey | Mukunda Johnson, Ken Snyder, Steven Velema, Hubert Lamontagne | 2009 | No encontrada (2) |
| ✓ | `superbossgaiden.sfc` | Super Boss Gaiden 1.2 | Chrono Moogle, Dieter Von Laser (D4S) | 2016 (3) | No encontrada |
|  | `tchouv2.smc` | Tchou 2 | Debray Matthieu (Dieudunet) | 2012 | No encontrada |

1. El `.txt` dice 2018 y `gamelist.xml` dice 2008.
2. Hubo edición posterior en cartucho: [Rockfall](https://www.mobygames.com/game/130651/rockfall),
   [Skipp and Friends](https://tasvideos.org/2465G). Conviene pedir permiso antes de redistribuir.
3. `gamelist.xml` dice 2009, pero la [prensa de su lanzamiento](https://www.nintendolife.com/news/2016/07/someone_has_actually_made_a_game_which_works_on_the_snes_playstation) es de julio de 2016.

«No encontrada» no equivale a dominio público: los derechos siguen siendo del autor.

### Verificar el origen de un archivo

Git identifica cada archivo por un hash; si coincide, es idéntico al de retrobrews:

```bash
git hash-object ~/retro-console/roms/*.s[fm]c
```

| Archivo | Hash |
|---|---|
| `astrohawk.smc` | `3c88d8c9f7c3cbde8c789bd7795908c05774b20c` |
| `blt.sfc` | `84f0e6463329621b595b49d2d0724a27fb9be097` |
| `bucket.smc` | `c6f7dd096f2e16aeb2e783d91ea678f3ec9bc63e` |
| `furryrpg.sfc` | `278e1ae06f3bdd98aa128ce483ed3ccb29f5a8ae` |
| `hilda.sfc` | `e7658280b11553f175ebca927f9231a0061e9033` |
| `horizontal-shooter.sfc` | `720f8808695a7417b815d96cc0207d9f8c33f2d9` |
| `jetpilotrising.sfc` | `52273553857848016b221969617414aaf02b0020` |
| `megafamilybros.smc` | `32acf3bd4bfb64a411f523161a2f4cf209e8c336` |
| `nwarpdaisakusen.smc` | `2f7bc9d7bc039d23fad6da028a9c7ecd1e949897` |
| `questformoney.sfc` | `41fa388b54c44c28c48001cc91c9657d49570db9` |
| `rockfall.smc` | `c851e7042a69632232c44602de83a71e77d9ee9c` |
| `saf.smc` | `5c75d178a0708391d702330a3403051f75dacd21` |
| `superbossgaiden.sfc` | `8de242f170d931b6fd558bf4f887410ec0b4e0c8` |
| `tchouv2.smc` | `7d20f9b6669c2ba50aa46ff07208e3c2bb5e719f` |

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

### Verificar los archivos descargados

```bash
sha256sum ~/retro-console/roms/*.nes ~/retro-console/roms/*.gba
```

| Archivo | SHA-256 |
|---|---|
| `openNES-Snake.nes` | `71792a9b4e4db52fb60df4633400301fac8f244f802b88d336b58e079c75acc7` |
| `thwaite.nes` | `a2df24d9c9f72e56c2fdc4c703becc47a5700ad0158da8208247635ebeb3779c` |
| `notebook-adventure.gba` | `944ed052a38f7d01df79bae760f102e5c19527471fc834c8986cb19606fb7e9a` |
| `beat-beast.gba` | `2a4986bdf6bd65601f1ae08f471d0aafc3e23d57f594162f77f351a1150e43eb` |

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
> No se suben a este repositorio ni al `.7z`, y el instalador no los descarga.
