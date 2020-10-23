#!/usr/bin/env bash

if [[ "$(arch)" == "x86_64" ]]; then
  TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/Windows%20Binaries/TkDND%202.8/tkdnd2.8-win32-x86_64.tar.gz/download"
else
  TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/Windows%20Binaries/TkDND%202.8/tkdnd2.8-win32-ix86.tar.gz/download"
fi
TKDND_WRAPPER_URL="https://sourceforge.net/projects/tkinterdnd/files/TkinterDnD2/TkinterDnD2-0.3.zip/download"

# Downloading the TkDnD library
wget -nv -nc --output-document tkdnd2.8.tar.gz "$TKDND_LIB_URL"
tar -xf tkdnd2.8.tar.gz
rm tkdnd2.8.tar.gz

# Downloading the TkDnD Python Wrapper
wget -nv -nc --output-document TkinterDnD2-0.3.zip "$TKDND_WRAPPER_URL"
unzip -q TkinterDnD2-0.3.zip
mv TkinterDnD2-0.3/TkinterDnD2 TkinterDnD2
rm TkinterDnD2-0.3.zip
rm -r TkinterDnD2-0.3