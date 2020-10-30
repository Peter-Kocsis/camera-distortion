#!/usr/bin/env python
"""
The parameters of the camera model can be calculated from images
taken about known calibration patterns. This module supports only checkerboard calibration pattern,
you can find one here:
https://github.com/Peter-Kocsis/camera-distortion/tree/main/calibration_images

The calibration images should be clear, not blurred and the calibration pattern needs to be visible.
"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = ["MIT License"]
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Released"

import argparse
import logging
import os
import sys

from camera_distortion.util.logger import init_logger
from camera_distortion import CameraModel, CalibrationPattern

logger = logging.getLogger(__file__)


def calibrate_argsparser() -> argparse.ArgumentParser:
    """
    Creates a parser for the script's arguments
    :returns: ArgumentParser object for parsing the script's arguments
    """
    parser = argparse.ArgumentParser(
        description="Script for determining the camera calibration parameters."
        "It requires images about the calibration pattern in different poses."
    )
    parser.add_argument(
        "-i",
        "--images",
        type=str,
        help="Path of the folder containing calibration images",
    )
    parser.add_argument(
        "-cam", "--camera", type=str, default="custom", help="The name of the camera"
    )
    parser.add_argument(
        "-n",
        "--num_images",
        type=int,
        default=20,
        help="Number of the images which needs to be collected for the calibration",
    )
    parser.add_argument(
        "-ch",
        "--calib_height",
        type=int,
        default=6,
        help="Number of the square blocks on the calibration image vertically",
    )
    parser.add_argument(
        "-cw",
        "--calib_width",
        type=int,
        default=9,
        help="Number of the square blocks on the calibration image horizontally",
    )
    parser.add_argument(
        "-cs",
        "--calib_size",
        type=float,
        default=25.0,
        help="Size of a single square block [cm]",
    )
    parser.add_argument(
        "-sp",
        "--show_points",
        action="store_true",
        default=False,
        help="Show calibration points",
    )
    return parser


def calibrate(
    image_folder_path: str,
    calib_pattern: CalibrationPattern,
    camera_name: str,
    show_points: bool,
) -> str:
    """
    This function determines the camera calibration parameters using 'png' and 'jpg'
    calibration images about a checkerboard calibration image.
    It is assumed that the checkerboard squares are square.
    The checkerboard corners are located on the grayscale image. If the points are not found,
    the image is skipped.

    :param image_folder_path: Path of the folder containing calibration image_pathes
    :param calib_pattern: The used calibration pattern
    :param camera_name: The name of the camera
    :param show_points: Indicates whether to show calibration points or not
    :returns: Path to the created parameter file
    """
    # Calculate the camera parameters
    camera_parameters, total_reproj_error = CameraModel.from_images(
        image_folder_path, calib_pattern, camera_name, show_points
    )

    # Show parameters
    logger.debug("Camera parameters: %s", camera_parameters)

    # Save data
    parameter_file = os.path.join(image_folder_path, "params.json")
    logger.debug("Saving camera parameters to %s", parameter_file)
    camera_parameters.save(parameter_file)

    logger.info(
        "Calibration finished, total reprojection error: %s, parameters saved to %s",
        total_reproj_error,
        parameter_file,
    )
    return parameter_file


if __name__ == "__main__":
    arguments = calibrate_argsparser().parse_args(sys.argv[1:])
    init_logger(logger)
    calibration_pattern = CalibrationPattern(
        calib_width=arguments.calib_width,
        calib_height=arguments.calib_height,
        calib_size=arguments.calib_size,
    )
    calibrate(
        image_folder_path=arguments.images,
        calib_pattern=calibration_pattern,
        camera_name=arguments.camera,
        show_points=arguments.show_points,
    )
