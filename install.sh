#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
APP_HOME="${AIPROJ_HOME:-"$HOME/.aiproj"}"
BIN_DIR="${AIPROJ_BIN_DIR:-"$HOME/.local/bin"}"

case "$APP_HOME" in
  ""|"/"|"$HOME")
    echo "Refusing unsafe AIPROJ_HOME: $APP_HOME" >&2
    exit 1
    ;;
esac

mkdir -p "$APP_HOME" "$BIN_DIR"

if [ "$SCRIPT_DIR" = "$APP_HOME" ]; then
  echo "Source and target are the same directory; skipping package copy."
elif command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "$SCRIPT_DIR/" "$APP_HOME/"
else
  rm -rf "$APP_HOME"
  mkdir -p "$APP_HOME"
  cp -R "$SCRIPT_DIR/." "$APP_HOME/"
fi

cat > "$BIN_DIR/aiproj" <<EOF
#!/usr/bin/env sh
exec python3 "$APP_HOME/bin/aiproj.py" "\$@"
EOF
chmod +x "$BIN_DIR/aiproj"

python3 "$APP_HOME/bin/aiproj.py" install-global --kit-root "$APP_HOME" --force

echo "Installed aiproj to $APP_HOME"
echo "Command wrapper: $BIN_DIR/aiproj"
echo "Add $BIN_DIR to PATH if aiproj is not found."
