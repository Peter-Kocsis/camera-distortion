#!/usr/bin/env python
"""
GUI application for undistorting images and videos
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
import sys
import threading
import pygubu
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from typing import List, Iterable
from urllib.parse import urlparse

from camera_distortion.camera_model import CameraModel
from camera_distortion.undistortion.undistort import undistort_image, undistort_video
from util.io import find_images, find_videos

try:
    from TkinterDnD2 import *
except ImportError:
    pass

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    # noinspection PyUnresolvedReferences
    # noinspection PyProtectedMember
    PROJECT_PATH = sys._MEIPASS
    RESOURCE_PATH = PROJECT_PATH
except AttributeError:
    PROJECT_PATH = os.getcwd()
    RESOURCE_PATH = os.path.join(PROJECT_PATH, "gui")


def _flatten(list_to_flatten: list) -> list:
    """
    Flattens a list:
    :param list_to_flatten: The list to flatten
    :returns: The flattened list
    """
    return [item for sublist in list_to_flatten for item in sublist]


class CameraDistortionApp:
    """
    Class for the application.
    It is responsible for creating the GUI and handling the events.
    """
    logger = logging.getLogger(__name__)

    def __init__(self):
        """
        Initialize object.
        This method builds the GUI and binds the callbacks to the events
        """
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(RESOURCE_PATH)
        builder.add_from_file(os.path.join(RESOURCE_PATH, "camera_distortion.ui"))
        self.mainwindow = builder.get_object('application')
        if self._load_tkdnd():
            self._bind_dnd_targets()
        self._gui_update_interval = 100
        self._automatic_gui_update()
        builder.connect_callbacks(self)

    def _load_tkdnd(self):
        """
        Loads the tkdnd library, which is required for drag-and-drop support
        """
        if "TkinterDnD2" not in sys.modules:
            self.logger.warning("Tkdnd python wrapper not found, drag-and-drop won't be supported!")
            return False

        tkdndlib_project = os.path.join(PROJECT_PATH, 'tkdnd2.8')
        tkdndlib_env = os.environ.get('TKDND_LIBRARY')
        if os.path.exists(tkdndlib_project):
            tkdndlib = tkdndlib_project
        elif tkdndlib_env and os.path.exists(tkdndlib_env):
            tkdndlib = tkdndlib_env
        else:
            CameraDistortionApp.logger.warning(f"Tkdnd not found nor at {tkdndlib_project}, "
                                               f"neither under environment variable TKDND_LIBRARY, "
                                               f"drag-and-drop won't be supported!")
            return False
        try:
            self.mainwindow.tk.eval(f"global auto_path; lappend auto_path {{{tkdndlib}}}")
            self.mainwindow.tk.call('package', 'require', 'tkdnd')
        except tk.TclError:
            CameraDistortionApp.logger.warning("Unable to load tkdnd library.")
            return False
        return True

    def _bind_dnd_targets(self):
        """
        Binds the drag-and-drop callbacks
        """
        element_callback_dict = {"output_path_entry": self.on_output_path_dnd,
                                 "input_media_files": self.on_input_media_dnd,
                                 "camera_parameter_entry": self.on_camera_parameter_dnd}
        for element_name, callback in element_callback_dict.items():
            element = self.builder.get_object(element_name)
            element.drop_target_register(CF_HDROP)
            element.dnd_bind('<<Drop>>', callback)

    @staticmethod
    def _insert_elements_to_listbox(listbox: tk.Listbox, elements: Iterable):
        """
        Inserts elements to a listbox
        :param listbox: The listbox which should be extended
        :param elements: The elements to be inserted
        """
        for element in elements:
            listbox.insert(tk.END, element)
            listbox.itemconfig(tk.END, bg="cyan")

    def _find_and_add_files(self, listbox: tk.Listbox):
        """
        Browse for files and add to a listbox
        :param listbox: The listbox which should be extended with the browsed paths
        """
        files = fd.askopenfiles()
        file_names = [file.name for file in files]
        self._insert_elements_to_listbox(listbox, file_names)

    @staticmethod
    def _parse_uries(uri_pathes: str) -> List[str]:
        """
        Parse uries to correct path
        :param uri_pathes: The uries to be parsed
        :returns: The parsed paths
        """
        pathes = []
        uries: List[str] = uri_pathes.split()
        for uri in uries:
            p = urlparse(uri)
            pathes.append(os.path.abspath(os.path.join(p.netloc, p.path)))
        return pathes

    def _add_files_from_dnd(self, event):
        """
        Add paths to the listbox from drag-and-drop event
        :param event: The event object
        """
        listbox = event.widget
        pathes = self._parse_uries(event.data)
        self._insert_elements_to_listbox(listbox, pathes)

    def _set_path_from_dnd(self, event):
        """
        Callback for drag-and-drop on entry
        This method will place the dropped path if valid into the entry
        :param event: The event object
        """
        paths = self._parse_uries(event.data)
        if len(paths) > 1:
            messagebox.showerror(f"Invalid path",
                                 f"Only one path can be used as output, more was provided: {paths}")
            return
        elif len(paths) == 0:
            return

        event.widget.delete(0, tk.END)
        event.widget.insert(0, paths[0])

    # noinspection PyUnusedLocal
    def on_camera_parameters_button(self, event=None):
        """
        Callback for click on camera parameters button
        This method will start a browsing for a single file and place the path into the `camera_parameter_entry`
        :param event: The event object
        """
        output_path = fd.askopenfilename()

        output_path_entry: tk.Entry = self.builder.get_object("camera_parameter_entry")
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

    def on_camera_parameter_dnd(self, event):
        """
        Callback for drag-and-drop on camera parameters entry
        This method will place the dropped path if valid into the `camera_parameter_entry`
        :param event: The event object
        """
        return self._set_path_from_dnd(event)

    # noinspection PyUnusedLocal
    def on_input_media_button(self, event=None):
        """
        Callback for click on input media button
        This method will start a browsing for files or folders and place the paths into the `input_media_files` listbox
        :param event: The event object
        """
        file_list = self.builder.get_object("input_media_files")
        self._find_and_add_files(file_list)

    def on_input_media_dnd(self, event):
        """
        Callback for drag-and-drop on input media entry
        This method will place the dropped paths into the `input_media_files` listbox
        :param event: The event object
        """
        self._add_files_from_dnd(event)

    # noinspection PyUnusedLocal
    def on_output_path_button(self, event=None):
        """
        Callback for click on output path button
        This method will start a browsing for a single folder and place the path into the `output_path_entry`
        :param event: The event object
        """
        output_path = fd.askdirectory()

        output_path_entry: tk.Entry = self.builder.get_object("output_path_entry")
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

    def on_output_path_dnd(self, event):
        """
        Callback for drag-and-drop on output path entry
        This method will place the dropped path if valid into the `output_path_entry`
        :param event: The event object
        """
        return self._set_path_from_dnd(event)

    def _automatic_gui_update(self):
        """
        Automatically updates the GUI in every `self._gui_update_interval` milliseconds
        """
        self.mainwindow.update_idletasks()
        self.mainwindow.after(self._gui_update_interval, self._automatic_gui_update)

    def undistort(self):
        """
        Undistorts the media files in the input media listbox
        given the camera parameters defined in the camera parameters entry and
        saves to the output path defined in the output path entry
        """
        status_label: tk.Label = self.builder.get_object("status_label")
        image_progress_bar: ttk.Progressbar = self.builder.get_object("image_progress_bar")
        video_progress_bar: ttk.Progressbar = self.builder.get_object("video_progress_bar")

        camera_parameter_list: tk.Entry = self.builder.get_object("camera_parameter_entry")
        parameters_file = camera_parameter_list.get()
        if len(parameters_file) == 0:
            status_label.config(text=f"Unable to start undistortion, no parameter file has been given!")

        input_media_list: tk.Listbox = self.builder.get_object("input_media_files")
        media_pathes = list(input_media_list.get(0, tk.END))
        if len(media_pathes) == 0:
            status_label.config(text=f"Unable to start undistortion, no input media has been given!")

        output_path_entry: tk.Entry = self.builder.get_object("output_path_entry")
        out_folder = output_path_entry.get()
        if len(out_folder) == 0:
            status_label.config(text=f"Unable to start undistortion, no output path has been given!")

        crop = 0

        all_images = [find_images(media_path) for media_path in media_pathes]
        all_videos = [find_videos(media_path) for media_path in media_pathes]

        num_images = len(_flatten(all_images))
        num_videos = len(_flatten(all_videos))

        num_undist_images = 0
        num_undist_videos = 0

        camera_parameters = CameraModel.from_json(parameters_file)
        os.makedirs(out_folder, exist_ok=True)

        for idx, media_path in enumerate(media_pathes):
            input_media_list.itemconfig(idx, bg="gold")

            for image_path in all_images[idx]:
                rel_path = os.path.relpath(image_path, media_path)
                out_path = os.path.join(out_folder, os.path.dirname(rel_path))
                status_label.config(text=f"Undistorting {media_path} - {rel_path}")
                undistort_image(image_path, out_path, camera_parameters, crop)
                num_undist_images += 1
                image_progress_bar["value"] = 100 * num_undist_images/num_images

            for video_path in all_videos[idx]:
                rel_path = os.path.relpath(video_path, media_path)
                out_path = os.path.join(out_folder, os.path.dirname(rel_path))
                status_label.config(text=f"Undistorting {media_path} - {rel_path}")
                undistort_video(video_path, out_path, camera_parameters, crop)
                num_undist_videos += 1
                video_progress_bar["value"] = 100 * num_undist_videos/num_videos

            input_media_list.itemconfig(idx, bg="green")

        image_progress_bar["value"] = 0
        video_progress_bar["value"] = 0
        status_label.config(text=f"Undistortion finished")

    # noinspection PyUnusedLocal
    def on_start_button(self, event=None):
        """
        Callback for click on start button
        :param event: The event object
        """
        t1 = threading.Thread(target=self.undistort)
        t1.start()

    def run(self):
        """
        Starts the application
        """
        self.mainwindow.mainloop()


if sys.platform.lower().startswith('win'):
    """
    In windows the application fails to start if the it is built in `windowed` mode, because the the package moviepy
    tries to create a process in such a way, which causes error for the application built with pyinstaller.
    Until it is not solved, `non-windowed` version will be built and the command window in Windows is hidden during 
    running the application.
    """
    import ctypes

    def hide_console():
        """
        Hides the console window.
        """
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)

    def show_console():
        """
        Show console window
        """
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 1)
else:
    def hide_console():
        pass

    def show_console():
        pass


if __name__ == '__main__':
    app_frozen = getattr(sys, 'frozen', False)
    if app_frozen:
        hide_console()

    app = CameraDistortionApp()
    app.run()

    if app_frozen:
        show_console()
