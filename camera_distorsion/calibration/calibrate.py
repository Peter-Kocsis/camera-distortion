"""Script for determining the camera calibration parameters"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = []
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Beta"

import argparse
import logging
import os
import sys

# create logger
from camera_distorsion.camera_parameters import CameraParameters
from util import init_logger

logger = logging.getLogger(__file__)


def calibrate_argsparser() -> argparse.ArgumentParser:
    """Returns a parser for the script's arguments"""
    parser = argparse.ArgumentParser(description="Script for determining the camera calibration parameters."
                                                 "It requires images about the calibration template in different poses.")
    parser.add_argument("-i", "--images", type=str,
                        help="Path of the folder containing calibration images")
    parser.add_argument("-cam", "--camera", type=str, default="custom", help="The name of the camera")
    parser.add_argument("-n", "--num_images", type=int, default=20,
                        help="Number of the images which needs to be collected for the calibration")
    parser.add_argument("-ch", "--calib_height", type=int, default=6,
                        help="Number of the square blocks on the calibration image vertically")
    parser.add_argument("-cw", "--calib_width", type=int, default=9,
                        help="Number of the square blocks on the calibration image horizontally")
    parser.add_argument("-cs", "--calib_size", type=float, default=25.0,
                        help="Size of a single square block [cm]")
    parser.add_argument("-sp", "--show_points", action="store_true", default=False, help="Show calibration points")
    return parser


def calibrate(image_folder_path: str, calib_width: int, calib_height: int, calib_size: float, camera_name:str, show_points: bool):
    """
    This function determines the camera calibration parameters using 'png' and 'jpg' calibration image_pathes
    about a checkerboard calibration image which can be used for undistorsion later.
    It is assumed that the checkerboard squares are square.
    The checkerboard corners are located on the grayscale image. If the points are not found that image
    is skipped.

    :param image_folder_path: Path of the folder containing calibration image_pathes
    :param calib_width: Number of the square blocks on the calibration image horizontally
    :param calib_height: Number of the square blocks on the calibration image vertically
    :param calib_size: Size of a single square block [cm]
    :param camera_name: The name of the camera
    :param show_points: Indicates whether to show calibration points or not
    """
    # Calculate the camera parameters
    camera_parameters, total_reproj_error = CameraParameters.from_images(image_folder_path, calib_width, calib_height, calib_size,
                                                     camera_name, show_points)

    # Show parameters
    logger.debug(f"Camera parameters: {str(camera_parameters)}")

    # Save data
    parameter_file = os.path.join(image_folder_path, "params.json")
    logger.debug(f"Saving camera parameters to {parameter_file}")
    camera_parameters.save(parameter_file)

    logger.info(f"Calibration finished, total reprojection error: {total_reproj_error}, "
                f"parameters saved to {parameter_file}")


if __name__ == '__main__':
    arguments = calibrate_argsparser().parse_args(sys.argv[1:])
    init_logger(logger)
    calibrate(image_folder_path=arguments.images,
              calib_width=arguments.calib_width,
              calib_height=arguments.calib_height,
              calib_size=arguments.calib_size,
              camera_name=arguments.camera,
              show_points=arguments.show_points)
