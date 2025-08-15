#!/bin/sh
set -e

# Path for persistent data and marker
PERSISTENT_DIR="/app/data"
INSTALL_MARKER="$PERSISTENT_DIR/.installed"

# Ensure the persistent directory exists
mkdir -p "$PERSISTENT_DIR"

if [ ! -f "$INSTALL_MARKER" ]; then
    echo "Running installer..."
    python "setup/SMS_Installer.py" # Assuming this writes to $PERSISTENT_DIR
    touch "$INSTALL_MARKER"
    echo "Installation complete."
else
    echo "Installer already run. Skipping..."
fi

echo "Starting main application..."
exec python -m src.main