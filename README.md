# Camera distorsion
[![Build](https://github.com/Peter-Kocsis/camera-distortion/workflows/Build/badge.svg)](https://github.com/Peter-Kocsis/camera-distortion/actions?query=workflow%3ABuild)
[![Lint](https://github.com/Peter-Kocsis/camera-distortion/workflows/Lint/badge.svg)](https://github.com/Peter-Kocsis/camera-distortion/actions?query=workflow%3ALint)

A module for handling camera distorsion and undistorting images/videos by keeping the meta-data, originally developed for fisheye-removal. The project is written in Python, consists of a pacakge and an application for media undistortion. 

### Features
* **Collect calibration images from video**: Extract calibration images from video
* **Camera calibration**: Determine the intrinsic camera parameters from calibration images or calibration video
* **Image/video undistorsion**: Undistort images and videos given the intrinsic camera parameters but keeping the meta-data

## Python package

**Background**
Every images and videos which have been taken with real-world camera are distorted,
it means that the projection of the camera is not perfectly linear.
Simply speaking, the straight line become on the images curved.
This effect can be seen mainly on "fisheye" cams.

**Modelling distortion**
There are many ways to model camera distortions. The most wide-spread model is
the radial distortion model, which assumes that the distortion depends
on the distance from the optical center. This library supports currently only
the model used by [opencv](https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html)

**The camera model**
To handle the distortion one must obtain the camera model. In this project it is represented
by the `CameraModel` class. Obtaining the parameters for a specific model is called calibration.
It requires images taken with the camera and reference to calculate the optimal parameters.
Generally images from calibration pattern are taken, which contains known shapes and
easily markable corner points.

**Calibration images**
Currently, calibration images taken about checkerboard calibration pattern are supported.
Many (minimum 20 is recommended) images are required in different poses to calculate
precise camera parameters. These images can be taken individually, or a it can be extracted
from a video sequence using the `collect` module.

**Undistortion**
Given the camera model the images and videos can be undistorted, as a result the straight lines
should appear straight in the undistorted images.


The `camera_distortion` module is developed for easily undistort images and videos. Currently, it has three main submodules:

### Collect
Collecting calibration images from a video sequence. Given a video about a calibration pattern, images can be extracted and saved for the calibration. 

### Calibration 
Calculating intrinsic parameters from calibration images. 
The parameters of the camera model can be calculated from images taken about known calibration patterns. This module supports only checkerboard calibration pattern, you can find one here: https://github.com/Peter-Kocsis/camera-distortion/tree/main/calibration_images

The calibration images should be clear, not blurred and the calibration pattern needs to be visible.

### Undistortion
Knowing the camera distortion model one can find a mapping between the distorted
and undistorted point coordinates, which can be used to restore the undistorted image.
Generally, in favour of efficiency, the camera models uses invertible, which allows to calculate
the mapping in closed from.

### Installation
To install the python module, you can use the setup script
```bash
python setup.py install
```
or the provided requirements file
```bash
pip install -r requirements.txt
```

### Usage
#### Calibration
* **1.**: Capture video about the calibration pattern in which the pattern is moved around in many different poses, or capture calibration images and continue with step 3
* **2.**: Collect the calibration images from the video:
```bash
python -m collect.collect --video <PATH_TO_THE_CALIBRATION_VIDEO> --out_folder <PATH_TO_THE_OUTPUT>
```
* **3.**: Calculate the camera parameters:
```bash
python -m calibrate.calibrate --images <PATH_TO_THE_CALIBRATION_IMAGES>
```

#### Undistort images or videos
```bash
python -m unsitort.undistort <PATH_OR_PATHES_TO_THE_MEDIA_FILES_SEPARATED_BY_SPACE> --out_folder <PATH_TO_THE_OUTPUT> --parameters <PATH_TO_THE_CALIBRATION_FILE_FROM_STEP_3>
```

## Application
The GUI application provides easily usable interface for the full undistortion process.

## Download
The prebuilt binaries can be found in the latest release.

## Usage
**NOTE: For choosing any path, you can use Drag-and-Drop!**

**1.** Run the program! 

![Media undistortion app start]("0_empty_window.png)

**2.** Choose the calibration video! 

![Media undistortion calib video chosen]("1_choose_calib_video.png)

**3.** Start the calibration! 

![Media undistortion app start]("2_calib_images_collected.png)

**4.** Wait for finish!
 
![Media undistortion app start]("3_calib_finished.png)
 
**5.** Choose the input media and output path! 

![Media undistortion app start]("4_calib_finsihed_ready_to_start.png)

**6.** Start the undistortion! 

![Media undistortion app start]("5_starting_to_undistort.png)

**7.** Wait for every input to finish! 

![Media undistortion app start]("6_undistortion_in_progress.png)

**8.** Success! 

![Media undistortion app start]("7_successful_undistortion.png)

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
**Linux/MacOS**:
```bash
pyinstaller --name media_undistortion --add-data "./gui/camera_distortion.ui:." --add-data "./gui/icon.png:." --add-data "./tkdnd2.8:./tkdnd2.8" --hidden-import "pygubu.builder.tkstdwidgets" --add-binary "$(python -c 'import site; print(site.getsitepackages()[0])')/cv2/qt:./cv2/qt" --add-binary "$(python -c 'import site; print(site.getsitepackages()[0])')/opencv_python.libs:./opencv_python.libs" --hidden-import "pygubu.builder.ttkstdwidgets" --icon "./gui/icon.ico" --onefile ./gui/camera_distortion_app.py
```
**Windows**:
```bash
pyinstaller --name media_undistortion --add-data "./gui/camera_distortion.ui;." --add-data "./gui/icon.png;." --add-data "./tkdnd2.8;./tkdnd2.8" --hidden-import "pygubu.builder.tkstdwidgets" --add-binary "$(python -c 'import site; print(site.getsitepackages()[0])')/cv2/qt;./cv2/qt" --add-binary "$(python -c 'import site; print(site.getsitepackages()[0])')/opencv_python.libs;./opencv_python.libs" --hidden-import "pygubu.builder.ttkstdwidgets" --icon "./gui/icon.ico" --onefile ./gui/camera_distortion_app.py
```

## References
The package is based on the implementation of [The Eminenet Codefish](https://www.theeminentcodfish.com/gopro-calibration/).
