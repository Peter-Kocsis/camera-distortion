"""Script for determining the camera calibration parameters"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = []
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Beta"

import argparse
import datetime
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List
from PIL import Image, ExifTags
import moviepy.editor as mpe

import cv2
import numpy as np

# create logger
import pyexiv2

from camera_distorsion.camera_parameters import CameraParameters
from util import init_logger
from util.io import find_files, get_format, find_videos, find_images

logger = logging.getLogger(__file__)


def undistort_argsparser() -> argparse.ArgumentParser:
    """Returns a parser for the script's arguments"""
    parser = argparse.ArgumentParser(description="Script for determining the camera calibration parameters."
                                                 "It requires images about the calibration template in different poses.")
    parser.add_argument('image_path', type=str, nargs='+',
                        help='Pathes of the images')
    parser.add_argument("-p", "--parameters", type=str,
                        help="Path of the file containing the camera parameters")
    parser.add_argument("-c", "--crop", type=float, default=0.0, help="Ratio of cropping the undistorted image. "
                                                         "0 will crop all the black pixels, 1 keeps all the pixels")
    parser.add_argument("-o", "--out_folder", type=str, help="The output folder")
    return parser


def undistort_videos(video_pathes: List[str], out_folder: str, camera_parameters: CameraParameters, crop: float):
    for video_path in find_videos(video_pathes):
        logger.info(f"Undistorting video file {video_path}")
        # Read video
        video = mpe.VideoFileClip(video_path)
        file_name, ext = os.path.splitext(os.path.basename(video_path))

        if video is None:
            logger.error(f"Cannot open video file {video_path}!")
            continue
        logger.debug(f"Video file {video_path} read")

        # Undistort video
        undistorted_video = camera_parameters.undistort_video(video, crop)
        logger.debug(f"Video file {video_path} undistorted")

        # Save undistorted video
        undistorted_video_path = os.path.join(out_folder, f"{file_name}_undist{ext}")
        undistorted_video.write_videofile(filename=undistorted_video_path,
                                          bitrate=str(video.reader.bitrate) + 'K',
                                          audio=True,
                                          audio_fps=video.audio.fps,
                                          preset="medium",
                                          audio_codec='aac',
                                          audio_nbytes=video.audio.reader.nbytes,
                                          audio_bitrate=str(video.audio.reader.bitrate) + 'K',
                                          audio_bufsize=video.audio.buffersize)
        logger.info(f"Undistorted video file saved to {undistorted_video_path}")


def undistort_images(video_pathes: List[str], out_folder: str, camera_parameters: CameraParameters, crop: float):
    for image_path in find_images(video_pathes):
        logger.info(f"Undistorting image file {image_path}")

        # Read image
        image = Image.open(image_path)
        logger.debug(f"Image file {image_path} read")


        # Undistort image
        image_data = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        undistorted_image_data = camera_parameters.undistort_image(image_data, crop)
        undistorted_image = Image.fromarray(cv2.cvtColor(np.array(undistorted_image_data), cv2.COLOR_BGR2RGB))
        logger.debug(f"Image file {image_path} undistorted")

        # Save undistorted image
        image_name, ext = os.path.splitext(os.path.basename(image_path))
        undistorted_image_path = os.path.join(out_folder, f"{image_name}_undist{ext}")
        with open(undistorted_image_path, 'w') as outfile:
            undistorted_image.save(outfile, format=get_format(ext), exif=image.info['exif'])
        logger.info(f"Undistorted image file saved to {undistorted_image_path}")


def undistort(media_pathes: List[str], out_folder: str, parameters_file: str, crop: float):
    """
    This function undistorts media files given the camera parameters

    :param media_pathes: Pathes of the images
    :param parameters_file: Path of the camera parameter file
    :param crop: Ratio of cropping the undistorted image. 0 will crop all the black pixels, 1 keeps all the pixels
    """
    camera_parameters = CameraParameters.from_json(parameters_file)
    os.makedirs(out_folder, exist_ok=True)

    logger.info(f"Undistorting images")
    undistort_images(media_pathes, out_folder, camera_parameters, crop)

    logger.info(f"Undistorting videos")
    undistort_videos(media_pathes, out_folder, camera_parameters, crop)

    logger.info(f"Undistorsion finished!")




if __name__ == '__main__':
    arguments = undistort_argsparser().parse_args(sys.argv[1:])
    init_logger(logger)
    undistort(media_pathes=arguments.image_path,
              out_folder=arguments.out_folder,
              parameters_file=arguments.parameters,
              crop=arguments.crop)
