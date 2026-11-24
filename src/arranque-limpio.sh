#!/bin/bash
#
# Descripción: configura el arranque directo y limpio: sin login, sin mensajes
#              de Linux y sin arcoíris. Se puede repetir sin problema y al
#              final verifica cada punto.
# Uso:         sudo bash src/arranque-limpio.sh USUARIO
# Autor(es):   SegFaultPapi
# Licencia:    MIT (ver LICENSE)

set -euo pipefail
trap 'echo "[X] Se detuvo en la línea $LINENO: $BASH_COMMAND" >&2' ERR

usuario="${1:-}"
raiz="${RAIZ:-}"  # solo para pruebas: carpeta que sustituye a /
fuente="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ -n "$raiz" ] || [ "$(id -u)" -eq 0 ] || { echo "[X] Ejecútalo con sudo" >&2; exit 1; }
if [ -z "$usuario" ] || [ "$usuario" = root ] || ! id "$usuario" > /dev/null 2>&1; then
  echo "[X] Uso: sudo bash $0 USUARIO" >&2
  exit 1
fi
if [ -n "$raiz" ]; then casa="$raiz/home"; else casa="$(getent passwd "$usuario" | cut -d: -f6)"; fi

boot="$raiz/boot/firmware"
[ -f "$boot/cmdline.txt" ] || boot="$raiz/boot"
cmdline="$boot/cmdline.txt"
config="$boot/config.txt"
dropin="$raiz/etc/systemd/system/getty@tty1.service.d"
perfil="$raiz/etc/profile.d/retro-console.sh"

# --- Sesión automática en tty1 ---
mkdir -p "$dropin" "$(dirname "$perfil")"
# "zz-" se aplica al final: prevalece sobre el autologin de raspi-config.
rm -f "$dropin/retro-console.conf"
cat > "$dropin/zz-retro-console.conf" <<EOF
[Service]
Type=simple
ExecStart=
ExecStart=-/sbin/agetty --autologin $usuario --noissue --noclear %I \$TERM
EOF
sed "s|@USUARIO@|$usuario|g" "$fuente/retro-autostart.sh" > "$perfil"
chmod 644 "$perfil" "$dropin/zz-retro-console.conf"
touch "$casa/.hushlogin"

# --- Línea de comandos del kernel ---
[ -f "$cmdline.retro-bak" ] || cp "$cmdline" "$cmdline.retro-bak"
ceros="0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
opciones=(
  quiet loglevel=0 logo.nologo consoleblank=0
  vt.global_cursor_default=0
  systemd.show_status=false rd.systemd.show_status=false
  udev.log_level=0 rd.udev.log_level=0
  # Los 16 colores de la terminal en negro: lo que se escriba no se ve.
  "vt.default_red=$ceros" "vt.default_grn=$ceros" "vt.default_blu=$ceros"
)
nueva=""
for palabra in $(tr -d '\r' < "$cmdline"); do
  case "$palabra" in
    quiet|splash|plymouth.*|loglevel=*|logo.nologo|consoleblank=*) continue ;;
    vt.global_cursor_default=*|vt.default_*|systemd.show_status=*|rd.systemd.show_status=*) continue ;;
    udev.log_level=*|rd.udev.log_level=*) continue ;;
    console=tty1) palabra="console=tty3" ;;
  esac
  nueva+="$palabra "
done
nueva+="${opciones[*]}"
case " $nueva " in
  *" root="*) ;;
  *) echo "[X] $cmdline no tiene root=; no se modificó" >&2; exit 1 ;;
esac
printf '%s\n' "$nueva" > "$cmdline.nuevo"
mv "$cmdline.nuevo" "$cmdline"

# --- Arcoíris del firmware ---
[ -f "$config.retro-bak" ] || cp "$config" "$config.retro-bak"
if ! grep -q '^disable_splash=1' "$config"; then
  printf '\n[all]\ndisable_splash=1\n' >> "$config"
fi

# --- Servicios ---
if [ -z "$raiz" ]; then
  if [ -f /etc/systemd/system/retro-console.service ]; then
    systemctl disable retro-console.service || true
    rm -f /etc/systemd/system/retro-console.service
  fi
  systemctl daemon-reload
  systemctl set-default multi-user.target
  systemctl enable getty@tty1.service
fi
sync

# --- Verificación ---
fallas=0
revisar() {
  if eval "$2"; then echo "[OK] $1"; else echo "[X]  $1"; fallas=$((fallas + 1)); fi
}
revisar "Sesión automática de $usuario"    'grep -q -- "--autologin $usuario " "$dropin/zz-retro-console.conf"'
revisar "Inicio de la consola en tty1"     'grep -q startx "$perfil"'
revisar "Existe .xinitrc"                  '[ -f "$casa/.xinitrc" ]'
revisar "cmdline.txt en una sola línea"    '[ "$(wc -l < "$cmdline")" -eq 1 ]'
revisar "Mensajes de Linux ocultos"        'grep -q " quiet loglevel=0 " "$cmdline" && ! grep -qw "console=tty1" "$cmdline"'
revisar "Texto negro durante el arranque"  'grep -q "vt.default_blu=$ceros" "$cmdline"'
revisar "Sin arcoíris"                     'grep -q "^disable_splash=1" "$config"'
if [ -z "$raiz" ]; then
  revisar "systemd usa la sesión automática" 'systemctl cat getty@tty1 | grep "^ExecStart=-" | tail -n 1 | grep -q -- "--autologin $usuario "'
  revisar "Shell de $usuario es bash"        '[ "$(getent passwd "$usuario" | cut -d: -f7)" = /bin/bash ]'
fi
if [ "$fallas" -gt 0 ]; then
  echo "[X] Arranque limpio incompleto: $fallas punto(s)" >&2
  trap - ERR
  exit 1
fi
echo "[OK] Arranque limpio configurado"
