"""
Module for input and outpu handling
"""
__author__ = "Peter Kocsis"
__copyright__ = "Peter Kocsis"
__credits__ = ["MIT License"]
__version__ = "0.1"
__maintainer__ = "Peter Kocsis"
__email__ = "peter.kocsis@tum.de"
__status__ = "Released"

import logging
import os
from pathlib import Path
from typing import List, Union

logger = logging.getLogger(__file__)

__IMAGE_EXTENSIONS = [
    ".bmp",
    ".dib",  # Windows bitmaps
    ".jpeg",
    ".jpg",
    ".jpe",  # JPEG files
    ".jp2",  # JPEG 2000 files
    ".png",  # Portable Network Graphics
    ".webp",  # WebP
    ".pbm",
    ".pgm",
    ".ppm",
    ".pxm",
    ".pnm",  # Portable image format
    ".pfm",  # Pfiles
    ".sr",
    ".ras",  # Sun rasters
    ".tiff",
    ".tif",  # TIFF files
    ".exr",  # OpenEXR Image files
    ".hdr",
    ".pic",
]  # Radiance HDR
__IMAGE_EXTENSIONS.extend([ext.upper() for ext in __IMAGE_EXTENSIONS])


__VIDEO_EXTENSIONS = [".avi", ".mp4"]
__VIDEO_EXTENSIONS.extend([ext.upper() for ext in __VIDEO_EXTENSIONS])


def get_image_format(extension: str):
    """
    Gets the image format from extension
    :param extension: The extension
    :returns: The format
    """
    extension = extension.upper()
    if extension in (".JPG", ".JPE"):
        return "JPEG"

    return extension[1:]


# pylint: disable=unsubscriptable-object
def find_images(paths: Union[str, List[str]]) -> List[str]:
    """
    Finds image files
    :param paths: The path or list of paths where the image files to be searched
    :returns: The list of the paths of the found image files
    """
    logger.debug("Looking for image files in the pathes %s", paths)
    image_files = find_files(paths, __IMAGE_EXTENSIONS)
    logger.debug("Found image files: %s", image_files)
    return image_files


# pylint: disable=unsubscriptable-object
def find_videos(pathes: Union[str, List[str]]) -> List[str]:
    """
    Finds video files
    :param paths: The path or list of paths where the image files to be searched
    :returns: The list of the paths of the found found files
    """
    logger.debug("Looking for video files in the pathes %s", pathes)
    video_files = find_files(pathes, __VIDEO_EXTENSIONS)
    logger.debug("Found video files: %s", video_files)
    return video_files


# pylint: disable=unsubscriptable-object
def find_files(
    paths: Union[str, List[str]], extensions: Union[List[str], None] = None
) -> List[str]:
    """
    Finds files
    :param paths: The path or list of paths where the image files to be searched
    :param extensions: The extensions to be searched
    :returns: The list of the paths of the found image files
    """
    if extensions is None:
        extensions = [".*"]
    image_pathes = []
    if isinstance(paths, list):
        for path in paths:
            image_pathes.extend(find_files(path, extensions))
    else:
        path = paths
        if os.path.isdir(path):
            images_in_folder = [
                str(image_path)
                for extension in extensions
                for image_path in Path(path).rglob(f"*{extension}")
            ]
            image_pathes.extend(images_in_folder)
        elif os.path.splitext(path)[1] in extensions:
            image_pathes.append(path)
    return image_pathes
