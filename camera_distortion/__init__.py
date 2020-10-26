#!/usr/bin/env python
"""
Camera distortion library

**Background**
Every images and videos which have been taken with real-world camera are distorted,
it means that the projection of the camera is not perfectly linear.
Simply speaking, the straight line become on the images curved.
This effect can be seen mainly on "fisheye" cams.

**Modelling distortion**
There are many ways to model camera distortions. The most wide-spread model is
the radial distortion model, which assumes that the distortion depends
on the distance from the optical center. This library supports currently only
the model used by opencv, for further information please refer to
https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html

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
"""
from .camera_model import CameraModel, CalibrationPattern
