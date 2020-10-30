#!/usr/bin/env python
"""
The calibration images can be extracted from a calibration video.
The extracted images will be saved in a given folder and then they can be used for calibration.

The extracted images should be clear, not blurred and the calibration pattern needs to be visible.
"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = ["MIT License"]
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Released"

import os
import sys
import argparse
import logging
from typing import Union

import cv2

from camera_distortion.util.logger import init_logger

logger = logging.getLogger(__file__)


def collect_calibration_images_argsparser() -> argparse.ArgumentParser:
    """
    Creates a parser for the script's arguments
    :returns: ArgumentParser object for parsing the script's arguments
    """
    parser = argparse.ArgumentParser(
        description="Script for aquiring calibration images from video."
    )
    parser.add_argument(
        "-v", "--video", type=str, help="Path of the video for camera calibration"
    )
    parser.add_argument(
        "-o", "--out_folder", type=str, default=None, help="Path of the output folder"
    )
    parser.add_argument(
        "-n",
        "--num_images",
        type=int,
        default=20,
        help="Number of the images which needs to be collected for the calibration",
    )
    return parser


# pylint: disable=unsubscriptable-object
def collect_calibration_images(
    video_path: str, output_path: Union[str, None], num_of_images: int
):
    """
    Collects calibration images from a video file

    This function loads the video and starts playing it and looping until
    the required number of images are gathered. The playback speed can be adjusted
    by pressing + or -. To save the current image, press SPACE_BAR.
    The process can be interrupted by pressing ESC.

    :param video_path: Path to the video from that the calibration images will be aquired
    :param output_path: Path of the output folder (the same folder as the video if None)
    :param num_of_images: The number of images to be collected
    """
    logger.info(
        "Collecting images from video %s, "
        "press 'SPACE' to aquire image, '+' to accelerate, "
        "'-' to slow down the playback",
        video_path,
    )

    # Load the video file
    logger.debug("Loading video %s", video_path)
    video = cv2.VideoCapture(video_path)

    # Checks to see if a the video was properly imported
    if not video.isOpened():
        raise RuntimeError(f"Unable to open video {video_path}")

    logger.debug("Video %s loaded", video_path)

    # Collect metadata about the video.
    video_fps = video.get(cv2.CAP_PROP_FPS)
    original_frame_duration = 1 / (video_fps / 1000)
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Initializes variables
    collected_images = 0
    frame_duration_rates = [0.125, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    frame_duration_ratio_idx = 4

    # Create output folder
    if output_path is None:
        output_path = os.path.dirname(video_path)
    else:
        os.makedirs(output_path, exist_ok=True)

    # Video loop. Press SPACE to collect images. ESC terminates the function.
    while collected_images < num_of_images:
        success, image = video.read()
        current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)
        if not success:
            continue

        cv2.imshow("Video", image)
        key_code = cv2.waitKey(
            int(
                frame_duration_rates[frame_duration_ratio_idx] * original_frame_duration
            )
        )
        if collected_images == num_of_images:
            break
        # SPACE
        if key_code == 32:
            logger.debug("SPACE pressed, aquiring image")
            image_path = os.path.join(
                output_path, f"{video_name}_{collected_images}.png"
            )
            cv2.imwrite(image_path, image)
            logger.debug("Image saved to %s", image_path)
            collected_images += 1
            logger.info("%i images collected", collected_images)
        # +
        elif key_code == 43:
            logger.debug("+ pressed, accelerating playback")
            frame_duration_ratio_idx = max(0, frame_duration_ratio_idx - 1)
        # -
        elif key_code == 45:
            logger.debug("- pressed, decelerating playback")
            frame_duration_ratio_idx = min(
                len(frame_duration_rates) - 1, frame_duration_ratio_idx + 1
            )
        # ESC
        elif key_code == 27:
            logger.debug("ESC pressed, interrupting")
            logger.info("The image collection has been interrupted!")
            break

        # If the last frame is reached, reset the capture and the frame_counter
        if current_frame == video.get(cv2.CAP_PROP_FRAME_COUNT):
            # current_frame = 0  # Or whatever as long as it is the same as next line
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Clean up
    video.release()
    cv2.destroyAllWindows()

    logger.info("Calibration images collected from %s", video_path)


def main():
    arguments = collect_calibration_images_argsparser().parse_args(sys.argv[1:])
    init_logger(logger)
    collect_calibration_images(
        video_path=arguments.video,
        output_path=arguments.out_folder,
        num_of_images=arguments.num_images,
    )


if __name__ == "__main__":
    main()
