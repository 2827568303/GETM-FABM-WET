#!/bin/bash
# Install MSYS2 UCRT64 Fortran toolchain via TUNA mirror (no gpg, no default mirrors).
# Invoked from PowerShell:
#   C:\Users\dinod\.local\share\msys64\usr\bin\bash.exe /c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/tools/win-build/install_toolchain.sh
set -u
export PATH="/usr/bin:/ucrt64/bin:$PATH"
CONF=/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/tools/win-build/pacman-tuna.conf

echo "== installed (relevant) =="
pacman --config "$CONF" -Q 2>/dev/null | grep -E 'gcc-fortran|netcdf|cmake|ninja|hdf5|gcc-[0-9]|gcc-libs|binutils|crt|headers|gmp|mpfr|windows-default-manifest|winpthreads|libwinpthread|zlib|sz' | sort
echo "== end list =="

MISSING=()
for p in mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-netcdf-fortran mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-ninja; do
  pacman --config "$CONF" -Q "$p" >/dev/null 2>&1 || MISSING+=("$p")
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "== missing: ${MISSING[*]} — installing =="
  pacman --config "$CONF" -Sy --noconfirm --disable-download-timeout "${MISSING[@]}"
  echo "PACMAN_EXIT=$?"
else
  echo "ALL_INSTALLED"
fi

echo "== verify =="
for tool in gfortran cmake ninja nf-config; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "OK $tool -> $(command -v $tool)"
  else
    echo "MISSING $tool"
  fi
done
ls /ucrt64/bin/ | grep -i netcdf || echo "(no netcdf dlls)"
