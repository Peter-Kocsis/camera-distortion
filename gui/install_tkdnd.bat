@echo OFF

if "%PROCESSOR_ARCHITECTURE%"=="AMD64"; then
  set TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/Windows%%20Binaries/TkDND%%202.8/tkdnd2.8-win32-x86_64.tar.gz/download"
else
  set TKDND_LIB_URL="https://sourceforge.net/projects/tkdnd/files/Windows%%20Binaries/TkDND%%202.8/tkdnd2.8-win32-ix86.tar.gz/download"
fi
set TKDND_WRAPPER_URL="https://sourceforge.net/projects/tkinterdnd/files/TkinterDnD2/TkinterDnD2-0.3.zip/download"

Rem Downloading the TkDnD library
curl -L --output tkdnd2.8.tar.gz "%TKDND_LIB_URL%"
7z e tkdnd2.8.tar.gz  && 7z x tkdnd2.8.tar
del /q tkdnd2.8.tar.gz
del /q tkdnd2.8.tar

Rem Downloading the TkDnD Python Wrapper
curl -L --output TkinterDnD2-0.3.zip "%TKDND_WRAPPER_URL%"
7z x TkinterDnD2-0.3.zip
move TkinterDnD2-0.3/TkinterDnD2 TkinterDnD2
del /q TkinterDnD2-0.3.zip
rmdir /s /q TkinterDnD2-0.3