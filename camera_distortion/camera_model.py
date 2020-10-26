#!/usr/bin/env python
"""
Module for handling the camera model.
This module supports only currently only the model used by opencv, for further information please refer to
https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = ["MIT License"]
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Released"

from typing import Union, List, Tuple

import cv2
import json
import logging
import numpy as np

from moviepy.video.io.VideoFileClip import VideoFileClip

from util import serialize
from util.io import find_files


class CameraModel:
    """
    Class for handling the camera model.
    It is responsible to calculate the parameters from images, save, load them and use it for undistortion.
    This class stores the unscaled intrinsic matrix, the distortion coefficients and the name fo the camera
    .. seealso:: https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
    """
    logger = logging.getLogger(__name__)

    def __init__(self):
        """
        Initialize empty object.
        """
        self.camera_name = None
        self.intrinsic_matrix = None
        self.distortion_coeffs = None

    @classmethod
    def from_values(cls,
                    camera_name: str,
                    intrinsic_matrix: np.ndarray,
                    distorsion_coeffs: np.ndarray) -> 'CameraModel':
        """
        Create object from known parameters.
        :param camera_name: The name of the camera
        :param intrinsic_matrix: The unscaled intrinsic camera matrix
        :param distorsion_coeffs: The distortion coefficients defined by opencv
        :returns: New object with the given values
        """
        obj = cls()
        obj.camera_name = camera_name
        obj.intrinsic_matrix = intrinsic_matrix
        obj.distortion_coeffs = distorsion_coeffs
        return obj

    @classmethod
    def from_dict(cls, param_dict: dict) -> 'CameraModel':
        """
        Create object from known parameters as a dictionary
        :param param_dict: The dictionary which contains the attributes
        :returns: New object with the given values
        """
        obj = cls()
        for param, value in param_dict.items():
            if hasattr(obj, param):
                setattr(obj, param, value)
            else:
                raise AttributeError(f"The class {__name__} has no attribute {param}")
        return obj

    @classmethod
    def from_images(cls,
                    image_pathes: Union[List[str], str],
                    calib_width: int,
                    calib_height: int,
                    calib_size: float,
                    camera_name: str = "custom",
                    show_points: bool = False) -> Tuple['CameraModel', float]:
        """
        Create object by obtaining parameters from calibration images.
        :param image_pathes: Path or list of pathes to images or folders containing the calibration images
        :param calib_width: The number of rectangles on the calibration pattern horizontally
        :param calib_height: The number of rectangles on the calibration pattern vertically
        :param calib_size: The size of one calibration rectangle in [mm]
        :param camera_name: The name of the camera, default: "custom"
        :param show_points: Indicates whether to show the extracted points or not
        :returns: New object with the parameters obtained from the calibration images and the reprojection error
        :raise: Runtime error if none of the images contained information for the calibration,
                i.e. no calibration pattern could be recognized on any of them
        """
        # Find images
        image_pathes = find_files(image_pathes)
        n_images = len(image_pathes)
        cls.logger.info(f"Calculating camera calibration from {image_pathes} - {n_images} images found")

        # Initializing variables
        n_calib_points = calib_width * calib_height
        calib_object_points = []
        calib_det_points = []
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
        grey_image = None
        image_size = None
        valid_images = 0

        # prepare object points based on the actual dimensions of the calibration board
        # like (0,0,0), (25,0,0), (50,0,0) ....,(200,125,0)
        calibration_object_point = np.zeros((n_calib_points, 3), np.float32)
        calibration_object_point[:, :2] = np.mgrid[0:(calib_width * calib_size):calib_size,
                                                   0:(calib_height * calib_size):calib_size].T.reshape(-1, 2)

        # Loop through the image_pathes. Find checkerboard corners and save the data to calib_det_points.
        for image_path in image_pathes:

            # Loading image_pathes
            cls.logger.debug(f"Loading image {image_path}")
            image = cv2.imread(str(image_path))
            height, width, depth = image.shape
            image_size = np.array([width, height])

            # Converting to grayscale
            cls.logger.debug(f"Converting image {image_path} to grayscale")
            grey_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Find chessboard corners
            cls.logger.debug(f"Find chessboard corners on image {image_path}")
            found, corners = cv2.findChessboardCorners(grey_image, (calib_width, calib_height),
                                                       cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE)

            if not found:
                cls.logger.warning(f"Cannot find corners on image {image_path}")
                continue

            cls.logger.debug(f"{len(corners)} corners have been found on image {image_path}")

            # Add the "true" checkerboard corners
            calib_object_points.append(calibration_object_point)

            # Improve the accuracy of the checkerboard corners found in the image
            # and save them to the calib_det_points variable.
            cv2.cornerSubPix(grey_image, corners, (20, 20), (-1, -1), criteria)
            calib_det_points.append(corners)

            valid_images += 1

            if show_points:
                # Draw chessboard corners
                cv2.drawChessboardCorners(image, (calib_width, calib_height), corners, found)

                # Show the image with the chessboard corners overlaid.
                cv2.imshow("Corners", image)

            # Check for interruption
            key_code = cv2.waitKey(0)
            if key_code == 27:
                cls.logger.debug(f"ESC pressed, interrupting")
                raise RuntimeError("The image collection has been interrupted!")

        if show_points:
            cv2.destroyWindow("Corners")

        if valid_images == 0:
            raise RuntimeError("Unable to calculate the parameters, "
                               "none of the given images contained recognizable calibration pattern!")

        # Calibrate the camera
        cls.logger.info("Calibration points collected, calculating camera parameters")
        ret, intrinsic_matrix, dist_coefficients, rvecs, tvecs = \
            cv2.calibrateCamera(calib_object_points, calib_det_points, grey_image.shape[::-1], None, None)

        obj = cls.from_values(camera_name, intrinsic_matrix / image_size, dist_coefficients)

        # Calculate the total reprojection error.  The closer to zero the better.
        tot_error = 0
        for i in range(len(calib_object_points)):
            image_points2, _ = \
                cv2.projectPoints(calib_object_points[i], rvecs[i], tvecs[i], intrinsic_matrix, dist_coefficients)
            error = cv2.norm(calib_det_points[i], image_points2, cv2.NORM_L2) / len(image_points2)
            tot_error += error
        total_reproject_error = tot_error / len(calib_object_points)

        return obj, total_reproject_error

    @classmethod
    def from_json(cls, path: str) -> 'CameraModel':
        """
        Create object from parameters specified in a JSON file
        :param path: Path to the JSON file
        :returns: New object with the given values
        """
        with open(path, 'r') as infile:
            data = json.load(infile)
            numpy_members = ["intrinsic_matrix", "distortion_coeffs"]
            for numpy_member in numpy_members:
                data[numpy_member] = np.array(data[numpy_member])
            return cls.from_dict(data)

    def save(self, path: str):
        """
        Save the object as JSON
        :param path: The path to the JSON file
        """
        with open(path, 'w') as outfile:
            json.dump(self, outfile, default=serialize, indent=2)

    def scaled_intrinsic_matrix(self, image_size: Tuple[int, int]) -> np.ndarray:
        """
        Calculates the scaled intrinsic matrix given the image size
        :param image_size: The size of the image (width, height)
        :returns: The intrinsic matrix scaled for the given image size
        """
        factor = np.append(np.array(image_size), 1)
        return self.intrinsic_matrix * factor[:, None]

    def get_undistortion_mapping(self, image_size: Tuple[int, int], crop: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates the mapping between the distorted and undistorted image
        :param image_size: The size of the image (width, height)
        :param crop: Cropping parameter for the undistortion
        :returns: Mapping in x and y directions
        """
        intrinsic_matrix = self.scaled_intrinsic_matrix(image_size)

        # Scale the images and create a rectification map.
        new_mat, roi = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, self.distortion_coeffs,
                                                     image_size, alpha=crop, centerPrincipalPoint=1)
        return cv2.initUndistortRectifyMap(intrinsic_matrix, self.distortion_coeffs, None,
                                           new_mat, image_size, m1type=cv2.CV_32FC1)

    def undistort_video(self, video: VideoFileClip, crop: float) -> VideoFileClip:
        """
        Undistort a video
        :param video: The video to be undistorted
        :param crop: Cropping parameter for the undistortion
        :returns: Undistorted video object
        """
        width = video.w
        height = video.h

        mapx, mapy = self.get_undistortion_mapping((width, height), crop)

        def undistort(image):
            return cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

        return video.fl_image(undistort)

    def undistort_image(self, image: np.ndarray, crop: float) -> np.ndarray:
        """
        Undistort an image
        :param image: The image as numpy array
        :param crop: Cropping parameter for the undistortion
        :returns: Undistorted image as numpy array
        """
        height, width, channels = image.shape

        mapx, mapy = self.get_undistortion_mapping((width, height), crop)
        # Undistort the image
        return cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

    def __str__(self):
        """
        String representation of the object
        """
        return f"{self.camera_name}\n" \
               f"Unscaled intrinsic matrix:\n{self.intrinsic_matrix}\n" \
               f"Distortion coeffs: {self.distortion_coeffs}"
