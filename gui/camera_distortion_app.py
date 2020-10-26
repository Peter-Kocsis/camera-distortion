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
import re
import sys
import threading
import tkinter as tk
import tkinter.ttk as ttk
from enum import Enum
from tkinter import filedialog as fd
from tkinter import messagebox
from typing import List, Iterable
from urllib.parse import urlparse

import pygubu
from camera_distortion.calibration import calibrate
from camera_distortion.camera_model import CameraModel
from camera_distortion.collect import collect_calibration_images
from camera_distortion.undistortion.undistort import undistort_image, undistort_video
from util import init_logger
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


class _PathType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


_FILEDIALOG_ASK_PATH = {_PathType.FILE: fd.askopenfilename,
                        _PathType.DIRECTORY: fd.askdirectory}


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
        self.status_label: tk.Label = self.builder.get_object("status_label")
        if self._load_tkdnd():
            self._bind_dnd_targets()
        self._gui_update_interval = 100
        self._automatic_gui_update()
        builder.connect_callbacks(self)
        self._bind_entry_change_callbacks()

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

    def _bind_entry_change_callbacks(self):
        """
        Binds the entry-change callbacks
        """
        var_callback_dir = {"camera_parameter_entry_var": self._on_camera_parameter_entry,
                            "calibrate_entry_var": self._on_calibrate_entry}
        for variable_name, callback in var_callback_dir.items():
            variable: tk.StringVar = self.builder.get_variable(variable_name)
            variable.trace_add("write", callback)

    def _bind_dnd_targets(self):
        """
        Binds the drag-and-drop callbacks
        """
        element_callback_dict = {"collect_entry": self._on_dnd_entry,
                                 "calibrate_entry": self._on_dnd_entry,
                                 "camera_parameter_entry": self._on_dnd_entry,
                                 "output_path_entry": self._on_dnd_entry,
                                 "input_media_files": self._on_dnd_list}
        for element_name, callback in element_callback_dict.items():
            element = self.builder.get_object(element_name)
            element.drop_target_register(DND_ALL)
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
        pattern = "{(.*?)}|([^ ]+)"
        for match in re.finditer(pattern, uri_pathes):
            groups = match.groups()
            uri = groups[0] or groups[1]
            p = urlparse(uri)
            pathes.append(os.path.abspath(os.path.join(p.netloc, p.path)))
        return pathes

    @staticmethod
    def _enable_frame(frame):
        """
        Set frame and it's children to enabled state
        :param frame: Frame to enable
        """
        for child in frame.winfo_children():
            wtype = child.winfo_class()
            print(wtype)
            if wtype not in ('Frame', 'Labelframe'):
                child.configure(state='normal')
            else:
                CameraDistortionApp._enable_frame(child)

    @staticmethod
    def _disable_frame(frame):
        """
        Set frame and it's children to disabled state
        :param frame: Frame to disable
        """
        for child in frame.winfo_children():
            wtype = child.winfo_class()
            if wtype not in ('Frame', 'Labelframe'):
                child.configure(state='disable')
            else:
                CameraDistortionApp._disable_frame(child)

    @staticmethod
    def _on_dnd_list(event):
        """
        Add paths to the listbox from drag-and-drop event
        :param event: The event object
        """
        listbox = event.widget
        pathes = CameraDistortionApp._parse_uries(event.data)
        CameraDistortionApp._insert_elements_to_listbox(listbox, pathes)

    @staticmethod
    def _on_dnd_entry(event):
        """
        Callback for drag-and-drop on entry
        This method will place the dropped path if valid into the entry
        :param event: The event object
        """
        paths = CameraDistortionApp._parse_uries(event.data)
        if len(paths) > 1:
            messagebox.showerror(f"Invalid path",
                                 f"Only one path can be used as output, more was provided: {paths}")
            return
        elif len(paths) == 0:
            return

        event.widget.delete(0, tk.END)
        event.widget.insert(0, paths[0])

    @staticmethod
    def _on_input_frame_button(event, input_type: _PathType):
        """
        Callback for click on input frame button. It will ask for a path and set the frame's entry value
        :param event: The event object
        :param input_type: The type of the path which is requested
        """
        path = _FILEDIALOG_ASK_PATH[input_type]()

        entry = event.widget.master.children['!entry']
        entry.delete(0, tk.END)
        entry.insert(0, path)

    def _on_browse_collect_button(self, event=None):
        """
        Callback for click on browse collect button
        """
        self._on_input_frame_button(event, _PathType.FILE)

    def _on_collect_button(self, event=None):
        """
        Callback for click on collect button
        """
        self._collect()

    def _on_browse_calibrate_button(self, event=None):
        """
        Callback for click on browse calibrate button
        """
        self._on_input_frame_button(event, _PathType.DIRECTORY)

    def _on_calibrate_button(self, event=None):
        self._calibrate()

    def _on_calibrate_entry(self, name, index, mode):
        calibrate_entry: tk.Entry = self.builder.get_object("calibrate_entry")
        entry_value = calibrate_entry.get()
        if len(entry_value) != 0:
            self._disable_frame(self.builder.get_object("collect_frame"))
        else:
            self._enable_frame(self.builder.get_object("collect_frame"))


    # noinspection PyUnusedLocal
    def _on_browse_camera_parameters_button(self, event=None):
        """
        Callback for click on camera parameters button
        This method will start a browsing for a single file and place the path into the `camera_parameter_entry`
        :param event: The event object
        """
        self._on_input_frame_button(event, _PathType.FILE)

    def _on_camera_parameter_entry(self, name, index, mode):
        calibrate_entry: tk.Entry = self.builder.get_object("camera_parameter_entry")
        entry_value = calibrate_entry.get()
        if len(entry_value) != 0:
            self._disable_frame(self.builder.get_object("calibration_frame"))
        else:
            self._enable_frame(self.builder.get_object("calibration_frame"))

    # noinspection PyUnusedLocal
    def _on_browse_input_media_button(self, event=None):
        """
        Callback for click on input media button
        This method will start a browsing for files or folders and place the paths into the `input_media_files` listbox
        :param event: The event object
        """
        file_list = self.builder.get_object("input_media_files")
        self._find_and_add_files(file_list)

    # noinspection PyUnusedLocal

    def _on_browse_output_path_button(self, event=None):
        """
        Callback for click on output path button
        This method will start a browsing for a single folder and place the path into the `output_path_entry`
        :param event: The event object
        """
        self._on_input_frame_button(event, _PathType.DIRECTORY)

    def _automatic_gui_update(self):
        """
        Automatically updates the GUI in every `self._gui_update_interval` milliseconds
        """
        self.mainwindow.update_idletasks()
        self.mainwindow.after(self._gui_update_interval, self._automatic_gui_update)

    def _collect(self):
        self.status_label.config(text=f"Collecting calibration images")

        collect_entry: tk.Entry = self.builder.get_object("collect_entry")
        video_path = collect_entry.get()
        if len(video_path) == 0:
            self.status_label.config(text=f"Unable to collect images, no calibration video has been given!")
            return

        num_of_images = 2
        output_path = os.path.join(os.path.dirname(video_path), "calib_images")
        collect_calibration_images(video_path=video_path, output_path=output_path, num_of_images=num_of_images)

        calibrate_entry: tk.Entry = self.builder.get_object("calibrate_entry")
        calibrate_entry.delete(0, tk.END)
        calibrate_entry.insert(0, output_path)

        self.status_label.config(text=f"Calibration images collected")

    def _calibrate(self):
        self.status_label.config(text=f"Calibrating the camera model")

        calibrare_entry: tk.Entry = self.builder.get_object("calibrate_entry")
        image_folder_path = calibrare_entry.get()
        if len(image_folder_path) == 0:
            self.status_label.config(text=f"Unable to calibrate camera the model, "
                                          f"no calibration images have been given!")
            return

        calib_width = 9
        calib_height = 6
        calib_size = 25
        camera_name = "custom"
        show_points = False

        params_file = calibrate(image_folder_path=image_folder_path,
                                calib_width=calib_width,
                                calib_height=calib_height,
                                calib_size=calib_size,
                                camera_name=camera_name,
                                show_points=show_points)

        calibrate_entry: tk.Entry = self.builder.get_object("camera_parameter_entry")
        calibrate_entry.delete(0, tk.END)
        calibrate_entry.insert(0, params_file)
        self.status_label.config(text=f"Calibration finished")

    def _undistort(self):
        """
        Undistorts the media files in the input media listbox
        given the camera parameters defined in the camera parameters entry and
        saves to the output path defined in the output path entry
        """
        image_progress_bar: ttk.Progressbar = self.builder.get_object("image_progress_bar")
        video_progress_bar: ttk.Progressbar = self.builder.get_object("video_progress_bar")

        camera_parameter_list: tk.Entry = self.builder.get_object("camera_parameter_entry")
        parameters_file = camera_parameter_list.get()
        if len(parameters_file) == 0:
            self.status_label.config(text=f"Unable to start undistortion, no parameter file has been given!")
            return

        input_media_list: tk.Listbox = self.builder.get_object("input_media_files")
        media_pathes = list(input_media_list.get(0, tk.END))
        if len(media_pathes) == 0:
            self.status_label.config(text=f"Unable to start undistortion, no input media has been given!")
            return

        output_path_entry: tk.Entry = self.builder.get_object("output_path_entry")
        out_folder = output_path_entry.get()
        if len(out_folder) == 0:
            self.status_label.config(text=f"Unable to start undistortion, no output path has been given!")
            return

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
                self.status_label.config(text=f"Undistorting {media_path} - {rel_path}")
                undistort_image(image_path, out_path, camera_parameters, crop)
                num_undist_images += 1
                image_progress_bar["value"] = 100 * num_undist_images / num_images

            for video_path in all_videos[idx]:
                rel_path = os.path.relpath(video_path, media_path)
                out_path = os.path.join(out_folder, os.path.dirname(rel_path))
                self.status_label.config(text=f"Undistorting {media_path} - {rel_path}")
                undistort_video(video_path, out_path, camera_parameters, crop)
                num_undist_videos += 1
                video_progress_bar["value"] = 100 * num_undist_videos / num_videos

            input_media_list.itemconfig(idx, bg="green")

        image_progress_bar["value"] = 0
        video_progress_bar["value"] = 0
        self.status_label.config(text=f"Undistortion finished")

    # noinspection PyUnusedLocal
    def _on_start_button(self, event=None):
        """
        Callback for click on start button
        :param event: The event object
        """
        t1 = threading.Thread(target=self._undistort)
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
    init_logger(CameraDistortionApp.logger)
    app_frozen = getattr(sys, 'frozen', False)
    if app_frozen:
        hide_console()

    app = CameraDistortionApp()
    app.run()

    if app_frozen:
        show_console()
