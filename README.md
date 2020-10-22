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
TBD

### Usage
TBD

## Application

## Download

### Build the application locally
To build the `Media undistorsion` app, you should run the following command from the root of the repository:
```bash
pyinstaller --name media_undistorsion --add-data "./gui/camera_distorsion.ui:." --add-data "./gui/icon.png:." --hidden-import "pygubu.builder.tkstdwidgets" --hidden-import "pygubu.builder.ttkstdwidgets" --icon "./gui/icon.png" --windowed --onefile ./gui/camera_distorsion_app.py
```

## References
The package is based on the implementation of [The Eminenet Codefish](https://www.theeminentcodfish.com/gopro-calibration/).
