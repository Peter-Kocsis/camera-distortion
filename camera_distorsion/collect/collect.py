"""Module for collecting calibration images from video"""
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
from typing import Union

import cv2

# create logger
from util import init_logger

logger = logging.getLogger(__file__)

def calibrate_argsparser() -> argparse.ArgumentParser:
    """Returns a parser for the script's arguments"""
    parser = argparse.ArgumentParser(description="Script for aquiring calibration images from video.")
    parser.add_argument("-v", "--video", type=str, help="Path of the video for camera calibration")
    parser.add_argument("-o", "--out_folder ", type=str, default=None,
                        help="Path of the output folder")
    parser.add_argument("-n", "--num_images", type=int, default=20,
                        help="Number of the images which needs to be collected for the calibration")
    return parser


def collect_calibration_images(video_path: str, output_path: Union[str, None], num_of_images: int):
    """
    This function loads the video file into a data space called video. It then collects various
    meta-data about the file for later inputs. The function then enters a loop in which it loops
    through each image, displays the image and waits for a fixed amount of time before displaying
    the next image. The playback speed can be adjusted in the waitKey command.  During the loop
    checkerboard images can be collected by pressing the spacebar.  Each image will be saved as a
    *.png into the directory which stores this file.  The ESC key will terminate the function.
    The function will end once the correct number of images are collected or the video ends.
    For the processing step, try to collect all the images before the video ends.

    :param video_path: Path to the video from that the calibration images will be aquired
    :param output_path: Path of the output folder (the same folder as the video if None)
    :param num_of_images: The number of images to be collected
    """
    logger.info(f"Collecting images from video {video_path}, "
                f"press 'SPACE' to aquire image, '+' to accelerate, '-' to slow down the playback")

    # Load the video file
    logger.debug(f"Loading video {video_path}")
    video = cv2.VideoCapture(video_path)

    # Checks to see if a the video was properly imported
    if not video.isOpened():
        raise RuntimeError(f"Unable to open video {video_path}")
    else:
        logger.debug(f"Video {video_path} loaded")

    # Collect metadata about the video.
    video_fps = video.get(cv2.CAP_PROP_FPS)
    original_frame_duration = 1 / (video_fps / 1000)
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Initializes variables
    collected_images = 0
    frame_duration_rates = [0.125, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    frame_duration_ratio_idx = 4 # => 1.0

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

        cv2.imshow('Video', image)
        key_code = cv2.waitKey(int(frame_duration_rates[frame_duration_ratio_idx] * original_frame_duration))
        if collected_images == num_of_images:
            break
        # SPACE
        if key_code == 32:
            logger.debug(f"SPACE pressed, aquiring image")
            image_path = os.path.join(output_path, f"{video_name}_{collected_images}.png")
            cv2.imwrite(image_path, image)
            logger.debug(f"Image saved to {image_path}")
            collected_images += 1
            logger.info(str(collected_images) + ' images collected.')
        # +
        elif key_code == 43:
            logger.debug(f"+ pressed, accelerating playback")
            frame_duration_ratio_idx = max(0, frame_duration_ratio_idx - 1)
        # -
        elif key_code == 45:
            logger.debug(f"- pressed, decelerating playback")
            frame_duration_ratio_idx = min(len(frame_duration_rates) - 1, frame_duration_ratio_idx + 1)
        # ESC
        elif key_code == 27:
            logger.debug(f"ESC pressed, interrupting")
            raise RuntimeError("The image collection has been interrupted!")

        # If the last frame is reached, reset the capture and the frame_counter
        if current_frame == video.get(cv2.CAP_PROP_FRAME_COUNT):
            # current_frame = 0  # Or whatever as long as it is the same as next line
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Clean up
    video.release()
    cv2.destroyAllWindows()

    logger.info(f"Calibration images collected from {video_path}")


if __name__ == '__main__':
    arguments = calibrate_argsparser().parse_args(sys.argv[1:])
    init_logger(logger)
    collect_calibration_images(video_path=arguments.video,
                               output_path=arguments.out_folder,
                               num_of_images=arguments.num_images)
