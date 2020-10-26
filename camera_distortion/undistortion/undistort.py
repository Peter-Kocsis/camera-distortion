#!/usr/bin/env python
"""
Knowing the camera distortion model one can find a mapping between the distorted
and undistorted point coordinates, which can be used to restore the undistorted image.
To be efficient, the camera models uses invertible, which allows to calculate
the mapping in closed from.
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
from typing import List, Union

import cv2
import numpy as np
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip

from camera_distortion.camera_model import CameraModel
from util.logger import init_logger
from util.io import get_image_format, find_videos, find_images

logger = logging.getLogger(__file__)


def undistort_argsparser() -> argparse.ArgumentParser:
    """
    Creates a parser for the script's arguments
    :returns: ArgumentParser object for parsing the script's arguments
    """
    parser = argparse.ArgumentParser(
        description="Script for undistorting media files given the camera model."
    )
    parser.add_argument(
        "media_path",
        type=str,
        nargs="+",
        help="Path or list of paths of the media files",
    )
    parser.add_argument(
        "-p",
        "--parameters",
        type=str,
        help="Path of the file containing the camera parameters",
    )
    parser.add_argument(
        "-c",
        "--crop",
        type=float,
        default=0.0,
        help="Ratio of cropping the undistorted image. "
        "0 will crop all the black pixels, 1 keeps all the pixels",
    )
    parser.add_argument("-o", "--out_folder", type=str, help="The output folder")
    return parser


def undistort_video(
    video_path: str, out_folder: str, camera_model: CameraModel, crop: float
):
    """
    Undistorts a single video given the camera parameters but keeps the meta-data

    :param video_path: Path or list of paths of the media files
    :param out_folder: The output folder path
    :param camera_model: The camera model object
    :param crop: Ratio of cropping the undistorted image. 0 will crop all the black pixels,
                 1 keeps all the pixels
    """
    os.makedirs(out_folder, exist_ok=True)
    logger.info("Undistorting video file %s", video_path)
    # Read video
    video = VideoFileClip(video_path)
    file_name, ext = os.path.splitext(os.path.basename(video_path))

    if video is None:
        logger.error("Cannot open video file %s!", video_path)
        return
    logger.debug("Video file %s read", video_path)

    # Undistort video
    undistorted_video = camera_model.undistort_video(video, crop)
    logger.debug("Video file %s undistorted", video_path)

    # Save undistorted video
    undistorted_video_path = os.path.join(out_folder, f"{file_name}_undist{ext}")
    undistorted_video.write_videofile(
        filename=undistorted_video_path,
        bitrate=str(video.reader.bitrate) + "K",
        audio=True,
        audio_fps=video.audio.fps,
        preset="medium",
        audio_codec="aac",
        audio_nbytes=video.audio.reader.nbytes,
        audio_bitrate=str(video.audio.reader.bitrate) + "K",
        audio_bufsize=video.audio.buffersize,
    )
    logger.info("Undistorted video file saved to %s", undistorted_video_path)


def undistort_image(
    image_path: str, out_folder: str, camera_model: CameraModel, crop: float
):
    """
    Undistorts a single image given the camera parameters but keeps the meta-data

    :param image_path: Path or list of paths of the media files
    :param out_folder: The output folder path
    :param camera_model: The camera model object
    :param crop: Ratio of cropping the undistorted image. 0 will crop all the black pixels,
                 1 keeps all the pixels
    """
    os.makedirs(out_folder, exist_ok=True)
    logger.info("Undistorting image file %s", image_path)

    # Read image
    image = Image.open(image_path)
    logger.debug("Image file %s read", image_path)

    # Undistort image
    image_data = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    undistorted_image_data = camera_model.undistort_image(image_data, crop)
    undistorted_image = Image.fromarray(
        cv2.cvtColor(np.array(undistorted_image_data), cv2.COLOR_BGR2RGB)
    )
    logger.debug("Image file %s undistorted", image_path)

    # Save undistorted image
    image_name, ext = os.path.splitext(os.path.basename(image_path))
    undistorted_image_path = os.path.join(out_folder, f"{image_name}_undist{ext}")
    with open(undistorted_image_path, "w") as outfile:
        undistorted_image.save(
            outfile, format=get_image_format(ext), exif=image.info["exif"]
        )
    logger.info("Undistorted image file saved to %s", undistorted_image_path)


# pylint: disable=unsubscriptable-object
def undistort(
    media_path: Union[List[str], str],
    out_folder: str,
    parameters_file: str,
    crop: float,
):
    """
    Undistorts media files given the camera parameters but keeps the meta-data

    :param media_path: Path or list of pathes of the media files
    :param out_folder: The output folder path
    :param parameters_file: Path of the camera parameter file
    :param crop: Ratio of cropping the undistorted image. 0 will crop all the black pixels,
                 1 keeps all the pixels
    """
    camera_model = CameraModel.from_json(parameters_file)
    os.makedirs(out_folder, exist_ok=True)

    logger.info("Undistorting images")
    for image_path in find_images(media_path):
        undistort_image(image_path, out_folder, camera_model, crop)

    logger.info("Undistorting videos")
    for video_path in find_videos(media_path):
        undistort_video(video_path, out_folder, camera_model, crop)

    logger.info("Undistorsion finished!")


if __name__ == "__main__":
    arguments = undistort_argsparser().parse_args(sys.argv[1:])
    init_logger(logger)
    undistort(
        media_path=arguments.media_path,
        out_folder=arguments.out_folder,
        parameters_file=arguments.parameters,
        crop=arguments.crop,
    )
