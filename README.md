# Camera distorsion

A module for handling camera distorsion. Originally developed for fisheye-removal.

### Features
* Camera calibration: Determine the intrinsic camera parameters
* Image undistorsion
* Video undistorsion

## Python package

### Installation
TBD

#### Requirements
Tested python version: **3.7**
TBD

### Usage
TBD

## Application

## Download

### Local use and build

#### Requirements
##### TkDND - optional
TkDnD gives support for **drag-and-drop** in the GUI. If not provided, the application won't support drag-and-drop. It can be installed for system-wide use as described [here](https://stackoverflow.com/questions/25427347/how-to-install-and-use-tkdnd-with-python-tkinter-on-osx) or you can install it only for this application as follows:
* Download the TkDnD library and place in the root of the project 
    * Windows [64bit](https://sourceforge.net/projects/tkdnd/files/Windows%20Binaries/TkDND%202.8/tkdnd2.8-win32-x86_64.tar.gz/download) | 
[32bit](https://sourceforge.net/projects/tkdnd/files/Windows%20Binaries/TkDND%202.8/tkdnd2.8-win32-ix86.tar.gz/download)  
    * Linux [64bit](https://sourceforge.net/projects/tkdnd/files/Linux%20Binaries/TkDND%202.8/tkdnd2.8-linux-x86_64.tar.gz/download) | 
[32bit](https://sourceforge.net/projects/tkdnd/files/Linux%20Binaries/TkDND%202.8/tkdnd2.8-linux-ix86.tar.gz/download)  
    * [OSX](https://sourceforge.net/projects/tkdnd/files/OS%20X%20Binaries/TkDND%202.8/tkdnd2.8-OSX-MountainLion.tar.gz/download)
* Download the TkDnD Python wrapper and place the module TkinterDnD2 in the root of the project
    * [TkDnD python wrapper](https://sourceforge.net/projects/tkinterdnd/files/TkinterDnD2/TkinterDnD2-0.3.zip/download)

#### Build application file
In order to build the `Media undistorsion` app, you should run the following command from the root of the repository:
```bash
pyinstaller --name media_undistortion --add-data "./gui/camera_distorsion.ui;." --add-data "./gui/icon.png;." --add-data "./tkdnd2.8;./tkdnd2.8" --hidden-import "pygubu.builder.tkstdwidgets" --hidden-import "pygubu.builder.ttkstdwidgets" --icon "./gui/icon.ico" --onefile ./gui/camera_distortion_app.py
```

## References
The package is based on the implementation of [The Eminenet Codefish](https://www.theeminentcodfish.com/gopro-calibration/).
