from os import path

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(
    path.join(path.abspath(path.dirname(__file__)), "requirements.txt"),
    encoding="utf-8",
) as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="camera_distortion",
    version="0.1",
    author="Peter Kocsis",
    author_email="peter.kocsis@tum.de",
    description="Package for handling image distortion",
    keywords="vision camera action-camera fisheye undistortion distortion",
    license="GNU General Public License v3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Peter-Kocsis/camera-distortion",
    packages=setuptools.find_packages(exclude=["gui"]),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[(".", ["LICENSE"])],
    python_requires=">=3.7",
)
