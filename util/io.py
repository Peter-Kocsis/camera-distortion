import logging
import os
from collections import Iterable
from pathlib import Path
from typing import List, Union

logger = logging.getLogger(__file__)

__IMAGE_EXTENSIONS = ['.bmp', '.dib',  # Windows bitmaps
                      '.jpeg', '.jpg', '.jpe',  # JPEG files
                      '.jp2',  # JPEG 2000 files
                      '.png',  # Portable Network Graphics
                      '.webp',  # WebP
                      '.pbm', '.pgm', '.ppm', '.pxm', '.pnm',  # Portable image format
                      '.pfm',  # Pfiles
                      '.sr', '.ras',  # Sun rasters
                      '.tiff', '.tif',  # TIFF files
                      '.exr',  # OpenEXR Image files
                      '.hdr', '.pic', ]  # Radiance HDR
__IMAGE_EXTENSIONS.extend([ext.upper() for ext in __IMAGE_EXTENSIONS])


__VIDEO_EXTENSIONS = ['.avi', '.mp4']
__VIDEO_EXTENSIONS.extend([ext.upper() for ext in __VIDEO_EXTENSIONS])


def get_format(extension: str):
    extension = extension.upper()
    if extension == '.JPG' or extension == '.JPE':
        return 'JPEG'
    else:
        return extension[1:]


def find_images(pathes: Union[str, List[str]]):
    logger.debug(f"Looking for image files in the pathes {pathes}")
    image_files = find_files(pathes, __IMAGE_EXTENSIONS)
    logger.debug(f"Found image files: {image_files}")
    return image_files


def find_videos(pathes: Union[str, List[str]]):
    logger.debug(f"Looking for video files in the pathes {pathes}")
    video_files = find_files(pathes, __VIDEO_EXTENSIONS)
    logger.debug(f"Found video files: {video_files}")
    return video_files


def find_files(pathes: Union[str, List[str]], extensions: Union[List[str], None] = None):
    if extensions is None:
        extensions = ['.*']
    image_pathes = []
    if isinstance(pathes, List):
        for path in pathes:
            image_pathes.extend(find_files(path, extensions))
    else:
        path = pathes
        if os.path.isdir(path):
            images_in_folder = [str(image_path) for extension in extensions
                                for image_path in Path(path).rglob(f"*{extension}")]
            image_pathes.extend(images_in_folder)
        elif os.path.splitext(path)[1] in extensions:
            image_pathes.append(path)
    return image_pathes
