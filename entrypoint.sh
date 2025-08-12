#!/bin/sh
set -e

# Location to store the "installation done" marker
INSTALL_MARKER="/app/.installed"

if [ ! -f "$INSTALL_MARKER" ]; then
    echo "Running installer..."
    python "setup/SMS Installer.py"
    touch "$INSTALL_MARKER"
else
    echo "Installer already run. Skipping..."
fi

echo "Starting main application..."
exec python -m src.main

docker build -t sms-app .
docker run -it --name sms-container -v sms_data:/app sms-app
