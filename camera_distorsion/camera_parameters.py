"""Module for handling the intrinsic camera parameters"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = []
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Beta"

import logging
from pathlib import Path

import cv2
import numpy as np
import json
import moviepy.editor as mpe

from util import serialize
from util.io import find_files


class CameraParameters:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.camera_name = None
        self._intrinsic_matrix = None
        self.distorsion_coeffs = None
        self.calib_size = None

    @classmethod
    def from_values(cls,
                    camera_name: str,
                    intrinsic_matrix: np.ndarray,
                    distorsion_coeffs: np.ndarray,
                    image_size):
        obj = cls()
        obj.camera_name = camera_name
        obj._intrinsic_matrix = intrinsic_matrix
        obj.distorsion_coeffs = distorsion_coeffs
        obj.calib_size = image_size
        return obj

    @classmethod
    def from_dict(cls, param_dict: dict):
        """Initialize from dictionary"""
        obj = cls()
        for param, value in param_dict.items():
            if hasattr(obj, param):
                setattr(obj, param, value)
        return obj

    @classmethod
    def from_images(cls,
                    image_pathes: str,
                    calib_width: int,
                    calib_height: int,
                    calib_size: float,
                    camera_name: str = "custom",
                    show_points: bool = False):

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

        # prepare object points based on the actual dimensions of the calibration board
        # like (0,0,0), (25,0,0), (50,0,0) ....,(200,125,0)
        calib_object_point = np.zeros((n_calib_points, 3), np.float32)
        calib_object_point[:, :2] = np.mgrid[0:(calib_width * calib_size):calib_size,
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
            calib_object_points.append(calib_object_point)

            # Improve the accuracy of the checkerboard corners found in the image
            # and save them to the calib_det_points variable.
            cv2.cornerSubPix(grey_image, corners, (20, 20), (-1, -1), criteria)
            calib_det_points.append(corners)

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

        # Calibrate the camera
        cls.logger.info("Calibration points collected, calculating camera parameters")
        ret, intrinsic_matrix, distCoeff, rvecs, tvecs = \
            cv2.calibrateCamera(calib_object_points, calib_det_points, grey_image.shape[::-1], None, None)

        obj = cls.from_values(camera_name, intrinsic_matrix, distCoeff, image_size)

        # Calculate the total reprojection error.  The closer to zero the better.
        tot_error = 0
        for i in range(len(calib_object_points)):
            imgpoints2, _ = cv2.projectPoints(calib_object_points[i], rvecs[i], tvecs[i], intrinsic_matrix, distCoeff)
            error = cv2.norm(calib_det_points[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            tot_error += error
        total_reproj_error = tot_error / len(calib_object_points)

        return obj, total_reproj_error

    @classmethod
    def from_json(cls, path: str):
        with open(path, 'r') as infile:
            data = json.load(infile)
            numpy_members = ["_intrinsic_matrix", "distorsion_coeffs", "calib_size"]
            for numpy_member in numpy_members:
                data[numpy_member] = np.array(data[numpy_member])
            return cls.from_dict(data)

    def save(self, path: str):
        with open(path, 'w') as outfile:
            json.dump(self, outfile, default=serialize, indent=2)

    def intrinsic_matrix(self, image_size):
        factor = np.append(np.array(image_size) / self.calib_size, 1)
        return self._intrinsic_matrix * factor[:, None]

    def undistort_video(self, video: mpe.VideoFileClip, crop: float):
        width = video.w
        height = video.h
        video_size = (width, height)

        intrinsic_matrix = self.intrinsic_matrix(video_size)

        # Scale the images and create a rectification map.
        newMat, ROI = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, self.distorsion_coeffs,
                                                    video_size, alpha=crop, centerPrincipalPoint=1)
        mapx, mapy = cv2.initUndistortRectifyMap(intrinsic_matrix, self.distorsion_coeffs, None,
                                                 newMat, video_size, m1type=cv2.CV_32FC1)

        def undistort(image):
            return cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)

        return video.fl_image(undistort)

    def undistort_image(self, image: np.ndarray, crop: float):
        """
        This function undistorts an image given the camera parameters

        :param image_path: Path of the image
        :param crop: Crop parameter
        """
        height, width, channels = image.shape
        image_size = (width, height)

        intrinsic_matrix = self.intrinsic_matrix(image_size)

        # Scale the images and create a rectification map.
        newMat, ROI = cv2.getOptimalNewCameraMatrix(intrinsic_matrix, self.distorsion_coeffs,
                                                    image_size, alpha=crop, centerPrincipalPoint=1)
        mapx, mapy = cv2.initUndistortRectifyMap(intrinsic_matrix, self.distorsion_coeffs, None,
                                                 newMat, image_size, m1type=cv2.CV_32FC1)

        # Undistort the image
        return cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)


    def __str__(self):
        return f"{self.camera_name} intrinsic matrix:\n{self._intrinsic_matrix}," \
               f"\nDistorsion coeffs: {self.distorsion_coeffs}"