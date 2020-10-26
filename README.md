# Camera distorsion
![Build](https://github.com/Peter-Kocsis/camera-distortion/workflows/Build/badge.svg)
![Lint](https://github.com/Peter-Kocsis/camera-distortion/workflows/Lint/badge.svg)

A module for handling camera distorsion, originally developed for fisheye-removal. The project is written in Python, consists of a pacakge and an application for media undistortion. 

### Features
* **Camera calibration**: Determine the intrinsic camera parameters from calibration images or calibration video
* **Image undistorsion**: Undistort images given the intrinsic camera parameters
* **Video undistorsion**: Undistort videos given the intrinsic camera parameters

## Python package

The `camera_distortion` module is developed for easily undistort images and videos. Currently, it has three main submodules:

### Collect
Collecting calibration images from a video sequence

### Calibration 
Calculating intrinsic parameters from calibration images

### Undistortion
Undistorting images and videos given the intrinsic camera parameters

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
    
This steps can be done by calling the `install_tkdnd.sh` from the root of the project in case of Linux or MacOS systems or `install_tkdnd.bat` in case of Windows:

```bash
bash ./gui/install_tkdnd.sh
```

#### Build application file
In order to build the `Media undistorsion` app, you should run the following command from the root of the repository:
```bash
pyinstaller --name media_undistortion --add-data "./gui/camera_distortion.ui;." --add-data "./gui/icon.png;." --add-data "./tkdnd2.8;./tkdnd2.8" --hidden-import "pygubu.builder.tkstdwidgets" --hidden-import "pygubu.builder.ttkstdwidgets" --icon "./gui/icon.ico" --onefile ./gui/camera_distortion_app.py
```

## References
The package is based on the implementation of [The Eminenet Codefish](https://www.theeminentcodfish.com/gopro-calibration/).
