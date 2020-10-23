import logging
import os
import sys
import threading
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from typing import List
from urllib.parse import urlparse

import pygubu
from camera_distorsion.camera_parameters import CameraParameters
from camera_distorsion.undistorsion.undistort import undistort_image, undistort_video
from TkinterDnD2 import *
from util.io import find_images, find_videos

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    PROJECT_PATH = sys._MEIPASS
    RESOURCE_PATH = PROJECT_PATH
except Exception:
    PROJECT_PATH = os.getcwd()
    RESOURCE_PATH = os.path.join(PROJECT_PATH, "gui")

_flatten = lambda t: [item for sublist in t for item in sublist]


class CameraDistorsionApp:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(RESOURCE_PATH)
        builder.add_from_file(os.path.join(RESOURCE_PATH, "camera_distorsion.ui"))
        self.mainwindow = builder.get_object('application')
        if self._load_tkdnd():
            self.bind_dnd_targets()
        self._gui_update_interval = 100
        self._automatic_gui_update()
        builder.connect_callbacks(self)

    def _load_tkdnd(self):
        tkdndlib_project = os.path.join(PROJECT_PATH, 'tkdnd2.8')
        tkdndlib_env = os.environ.get('TKDND_LIBRARY')

        if os.path.exists(tkdndlib_project):
            tkdndlib = tkdndlib_project
        elif tkdndlib_env and os.path.exists(tkdndlib_env):
            tkdndlib = tkdndlib_env
        else:
            CameraDistorsionApp.logger.warning(f"Tkdnd not found nor at {tkdndlib_project}, "
                                               f"neither under environment variable TKDND_LIBRARY, "
                                               f"drag-and-drop won't be supported!")
            return False

        if tkdndlib:
            self.mainwindow.tk.eval('global auto_path; lappend auto_path {%s}' % tkdndlib)

        try:
            self.mainwindow.tk.call('package', 'require', 'tkdnd')
        except tk.TclError:
            CameraDistorsionApp.logger.warning('Unable to load tkdnd library.')
            return False
        return True

    def bind_dnd_targets(self):
        element_callback_dict = {"output_path_entry": self.on_output_path_dnd,
                                 "input_media_files": self.on_input_media_dnd,
                                 "camera_parameter_entry": self.on_camera_parameter_dnd}
        for element_name, callback in element_callback_dict.items():
            element = self.builder.get_object(element_name)
            element.drop_target_register(CF_HDROP)
            element.dnd_bind('<<Drop>>', callback)

    def _insert_elements_to_listbox(self, listbox, elements):
        for element in elements:
            listbox.insert(tk.END, element)
            listbox.itemconfig(tk.END, bg="cyan")

    def _find_and_add_files(self, listbox: tk.Listbox):
        files = fd.askopenfiles()
        file_names = [file.name for file in files]
        self._insert_elements_to_listbox(listbox, file_names)

    def _parse_uries(self, uri_pathes: str):
        pathes = []
        uries: List[str] = uri_pathes.split()
        for uri in uries:
            p = urlparse(uri)
            pathes.append(os.path.abspath(os.path.join(p.netloc, p.path)))
        return pathes

    def _add_files_from_dnd(self, event):
        listbox = event.widget
        pathes = self._parse_uries(event.data)
        self._insert_elements_to_listbox(listbox, pathes)

    def on_camera_parameters_button(self, event=None):
        output_path = fd.askopenfilename()

        output_path_entry: tk.Entry = self.builder.get_object("camera_parameter_entry")
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

    def on_camera_parameter_dnd(self, event=None):
        pathes = self._parse_uries(event.data)
        if len(pathes) > 1:
            messagebox.showerror(f"Invalid path",
                                 f"Only one path can be used as output, more was provided: {pathes}")
            return
        elif len(pathes) == 0:
            return

        event.widget.delete(0, tk.END)
        event.widget.insert(0, pathes[0])

    def on_input_media_button(self, event=None):
        file_list = self.builder.get_object("input_media_files")
        self._find_and_add_files(file_list)

    def on_input_media_dnd(self, event):
        self._add_files_from_dnd(event)

    def on_output_path_button(self, event=None):
        output_path = fd.askdirectory()

        output_path_entry: tk.Entry = self.builder.get_object("output_path_entry")
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, output_path)

    def on_output_path_dnd(self, event=None):
        pathes = self._parse_uries(event.data)
        if len(pathes) > 1:
            messagebox.showerror(f"Invalid path",
                                 f"Only one path can be used as output, more was provided: {pathes}")
            return
        elif len(pathes) == 0:
            return

        event.widget.delete(0, tk.END)
        event.widget.insert(0, pathes[0])

    def _automatic_gui_update(self):
        self.mainwindow.update_idletasks()
        self.mainwindow.after(self._gui_update_interval, self._automatic_gui_update)

    def undistort(self):
        camera_parameter_list: tk.Entry = self.builder.get_object("camera_parameter_entry")
        parameters_file = camera_parameter_list.get()

        input_media_list: tk.Listbox = self.builder.get_object("input_media_files")
        media_pathes = list(input_media_list.get(0, tk.END))

        output_path_entry: tk.Entry = self.builder.get_object("output_path_entry")
        out_folder = output_path_entry.get()

        status_label: tk.Label = self.builder.get_object("status_label")
        image_progress_bar: ttk.Progressbar = self.builder.get_object("image_progress_bar")
        video_progress_bar: ttk.Progressbar = self.builder.get_object("video_progress_bar")

        crop = 0

        all_images = [find_images(media_path) for media_path in media_pathes]
        all_videos = [find_videos(media_path) for media_path in media_pathes]

        num_images = len(_flatten(all_images))
        num_videos = len(_flatten(all_videos))

        num_undist_images = 0
        num_undist_videos = 0

        camera_parameters = CameraParameters.from_json(parameters_file)
        os.makedirs(out_folder, exist_ok=True)

        for idx, media_path in enumerate(media_pathes):
            input_media_list.itemconfig(idx, bg="gold")

            for image_path in all_images[idx]:
                rel_path = os.path.relpath(image_path, media_path)
                out_path = os.path.join(out_folder, os.path.dirname(rel_path))
                status_label.config(text=f"Undistorting {media_path} - {rel_path}")
                undistort_image(image_path, out_path, camera_parameters, crop)
                num_undist_images+=1
                image_progress_bar["value"] = 100 * num_undist_images/num_images

            for video_path in all_videos[idx]:
                rel_path = os.path.relpath(video_path, media_path)
                out_path = os.path.join(out_folder, os.path.dirname(rel_path))
                status_label.config(text=f"Undistorting {media_path} - {rel_path}")
                undistort_video(video_path, out_path, camera_parameters, crop)
                num_undist_videos+=1
                video_progress_bar["value"] = 100 * num_undist_videos/num_videos

            input_media_list.itemconfig(idx, bg="green")

        image_progress_bar["value"] = 0
        video_progress_bar["value"] = 0
        status_label.config(text=f"Undistortion finished")

    def on_start_button(self, event=None):
        t1 = threading.Thread(target=self.undistort)
        t1.start()

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    app = CameraDistorsionApp()
    app.run()
