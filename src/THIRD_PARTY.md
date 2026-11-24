# Fuentes externas

Consulta de las fuentes: 24 de noviembre de 2026. La licencia MIT de este repositorio cubre
solo el código propio; no cubre los programas ni las ROMs listados aquí.

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

Son las licencias declaradas por cada proyecto; deben cotejarse en `/usr/share/doc/<paquete>/copyright` de la Raspberry Pi.

## Referencia consultada

[RETROCONSOLA](https://github.com/jazminjia/RETROCONSOLA) (jazminjia, MIT): se estudió su
arquitectura. De ahí provienen las ideas de usar Mednafen y salir con VIEW + MENU; no se copió
código.

El formato de ID y de asignación del control se obtuvo leyendo el código fuente de Mednafen
1.32.1 (`Joystick_Linux.cpp`, `Joystick.cpp`); tampoco se copió código.

## Recursos propios

`src/assets/boot.wav` se sintetiza con `src/tools/generar_sonido.py`; no usa muestras externas.

## ROMs de retrobrews

Origen: https://github.com/retrobrews/snes-games (autores según su `README.md`; fechas y notas
según los `.txt` y `gamelist.xml` de cada juego).

> **Restricción:** retrobrews indica que las ROMs están aprobadas para distribución gratuita
> **solo en su sitio/proyecto** y pide contactar al autor para compartirlas. El repositorio no
> declara licencia general. Por eso **ninguna ROM se sube a este repositorio ni al `.7z`**;
> cada instalación las descarga de su origen.

La tabla es el catálogo de retrobrews. En «Usada» se marca lo que está en la consola.

| Usada | Archivo | Título | Autor(es) | Año | Licencia publicada |
|---|---|---|---|---|---|
| ☐ | `astrohawk.smc` | Astrohawk | Paul Lay | 2003 | No encontrada |
| ☐ | `blt.sfc` | BLT | Charles Doty (cdoty) | 2012 | No encontrada |
| ☐ | `bucket.smc` | Bucket | Sebastian Mihai | 2012 | No encontrada |
| ☐ | `furryrpg.sfc` | Furry RPG! | Ramsis | 2018 | Sin licencia formal; «open-source freeware» según [su autor](https://github.com/Ramsis-SNES/furryrpg) |
| ☐ | `hilda.sfc` | Hilda | Orochii Zouveleki (O_manko) | 2016 | No encontrada; [página](https://gamejolt.com/games/hilda/162284) |
| ☐ | `horizontal-shooter.sfc` | Horizontal Shooter | Marcus Rowe (Undisbeliever) | 2016 | Código MIT, imágenes CC0: [fuente](https://github.com/undisbeliever/horizontal-shooter) |
| ☐ | `jetpilotrising.sfc` | Jet Pilot Rising 1.1 | Dieter Von Laser (D4S) | 2008 o 2018 (1) | No encontrada |
| ☐ | `megafamilybros.smc` | Mega Family Bros | Debray Matthieu (Dieudunet) | 2012 | No encontrada |
| ☐ | `nwarpdaisakusen.smc` | N-Warp Daisakusen 1.0 | Dieter Von Laser (D4S) | 2009 | No encontrada; «descarga gratuita» según su `.txt` |
| ☐ | `questformoney.sfc` | Uwol, Quest For Money | Alekmaul, Mojon Twins, KungfuFurby | 2012 | No encontrada |
| ☐ | `rockfall.smc` | Rockfall | Paul Lay, Harvey A. Kong Tin | 1998 | No encontrada (2) |
| ☐ | `saf.smc` | Skipp And Friends: Unexpected Journey | Mukunda Johnson, Ken Snyder, Steven Velema, Hubert Lamontagne | 2009 | No encontrada (2) |
| ☐ | `superbossgaiden.sfc` | Super Boss Gaiden 1.2 | Chrono Moogle, Dieter Von Laser (D4S) | 2016 (3) | No encontrada |
| ☐ | `tchouv2.smc` | Tchou 2 | Debray Matthieu (Dieudunet) | 2012 | No encontrada |

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

## ROMs de itch.io

En itch.io la licencia la fija cada autor, así que debe copiarse de la página de cada juego.
**Pendiente del equipo:** el repositorio no registra qué títulos se descargaron.

| Archivo | Título | Autor | Versión / fecha | Licencia | URL de la página |
|---|---|---|---|---|---|
| _pendiente_ | | | | | |

## Pendiente de aclarar

- `src/retro_console.py` y los íconos no declaran origen. Si se adaptaron de otro proyecto,
  agregar autor, licencia, URL y «Modificado por: …».
- El comentario de `src/retro_console.py` usa `Rastan-SA1` como ejemplo. Ese título no está en
  retrobrews; si se usó, hay que documentar su origen y verificar que no derive de un juego
  comercial.
