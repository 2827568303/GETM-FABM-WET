#!/bin/bash
# Install GNU make (msys repo) for the "MSYS Makefiles" CMake generator.
set -u
export PATH="/usr/bin:/ucrt64/bin:$PATH"
CONF=/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/tools/win-build/pacman-tuna.conf
if ! command -v make >/dev/null 2>&1; then
  pacman --config "$CONF" -S --noconfirm --disable-download-timeout make
  echo "PACMAN_EXIT=$?"
fi
make --version | head -1
echo "MAKE_INSTALL_DONE"
