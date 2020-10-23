#!/usr/bin/env bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  if [[ "$(arch)" == "x86_64" ]]; then
    TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/Linux%20Binaries/TkDND%202.8/tkdnd2.8-linux-x86_64.tar.gz/download"
  else
    TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/Linux%20Binaries/TkDND%202.8/tkdnd2.8-linux-ix86.tar.gz/download"
  fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OSX
  TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/OS%20X%20Binaries/TkDND%202.8/tkdnd2.8-OSX-MountainLion.tar.gz/download"
else
  echo "Unsupported OS: $OSTYPE"
  exit 1
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