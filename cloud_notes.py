#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple note-taking app easy to back up via cloud.
The app itself is just a lightweight Python desktop app with a configurable folder to be used for notes.
It is this folder that you can back up to save your notes.
All the notes are just text files which the application reads and displays in a simple resizable window.

You will need Python3 with TkInter installed.
Just run the script. The default notes folder is `$HOME/.cloud_notes/notes`. To change it just click on "browse" button.
"""
from tkinter import Tk, Button, Frame, LEFT, RIGHT, X, TOP, BOTH, Text, filedialog
import os
import json
from time import time

COLOR_BACKGROUND = "#ffebb8"
COLOR_TEXT = "#21130d"

APP_TITLE = "Cloud Notes"
MAX_FILE_SIZE = 1024

cfg_name = "settings.cfg"
user_dir = os.path.expanduser("~")
cfg_dir = os.path.join(user_dir, ".cloud_notes")
cfg_path = os.path.join(cfg_dir, cfg_name)
default_notes_dir = os.path.join(cfg_dir, "notes")


class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.dismiss)

        self.title(APP_TITLE)
        self.minsize(300, 300)
        self.configure(background=COLOR_BACKGROUND)

        self.x = 200
        self.y = 200
        self.notes_dir = default_notes_dir
        self.note_file_name = None

        self.read_cfg()

        self.note_text = ""

        self.frame_btn = Frame(self, bg=COLOR_BACKGROUND)
        self.frame_btn.pack(fill=X, side=TOP)

        self.btn_prev = Button(self.frame_btn, text="<", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                               command=self.show_previous, width=3, height=1, pady=0, borderwidth=0)
        self.btn_prev.pack(side=LEFT)

        self.btn_next = Button(self.frame_btn, text=">", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                               command=self.show_next, width=3, height=1, pady=0, borderwidth=0)
        self.btn_next.pack(side=LEFT)

        self.btn_new = Button(self.frame_btn, text="New", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                              command=self.new_note, width=5, height=1, pady=0, borderwidth=0)
        self.btn_new.pack(side=LEFT)

        self.btn_delete = Button(self.frame_btn, text="Delete", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                                 command=self.delete_note, width=5, height=1, pady=0, borderwidth=0)
        self.btn_delete.pack(side=LEFT)

        self.btn_setup = Button(self.frame_btn, text="Browse", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                                command=self.select_notes_dir, width=5, height=1, pady=0, borderwidth=0)
        self.btn_setup.pack(side=RIGHT)

        self.display_text = Text(self, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, borderwidth=0, padx=5, pady=5)
        self.display_text.pack(padx=0, pady=0, fill=BOTH, expand=True)

        self.read_note(self.note_file_name)

        self.focus_force()

    def new_note(self):
        self.note_text = ""
        self.note_file_name = f"Note_{int(time())}"
        self.display_text.delete(1.0, "end")

    def delete_note(self):
        self.display_text.delete(1.0, "end")
        self.note_text = ""

        full_path = os.path.join(self.notes_dir, self.note_file_name)
        notes = self.list_notes()

        note_index = len(notes) - 1
        if len(notes) > 0:
            try:
                note_index = notes.index(self.note_file_name)
            except ValueError:
                note_index = len(notes) - 1

        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"ERROR: Could not remove file {full_path}. {e}")

        notes = self.list_notes()

        if note_index < len(notes):
            self.note_file_name = notes[note_index]
        elif len(notes) == 0:
            self.note_file_name = f"Note_{int(time())}"
        else:
            note_index = len(notes) - 1
            self.note_file_name = notes[note_index]

        self.read_note(self.note_file_name)

    def list_notes(self):
        notes = []

        if os.path.isdir(self.notes_dir):
            files = os.listdir(self.notes_dir)

            for file in files:
                full_path = os.path.join(self.notes_dir, file)
                if os.path.isfile(full_path):
                    file_stats = os.stat(full_path)
                    if file_stats.st_size < MAX_FILE_SIZE:
                        notes.append(file)

        notes.sort()
        return notes

    def read_note(self, file_name):
        self.display_text.delete(1.0, "end")

        if file_name is None:
            # No Note set. Set first one if exists
            notes = self.list_notes()
            if len(notes) > 0:
                self.note_file_name = notes[0]

        if file_name is None:
            # No notes available
            self.note_file_name = f"Note_{int(time())}"
        else:
            try:
                with open(os.path.join(self.notes_dir, file_name), 'r') as note:
                    self.note_text = note.read()
                    self.display_text.insert(1.0, self.note_text)
                    self.note_file_name = file_name
            except FileNotFoundError:
                # This note no longer exists. Remove from config.
                self.note_file_name = None
                self.save_cfg()
                self.note_file_name = f"Note_{int(time())}"

    def save_note(self):
        text = self.display_text.get("1.0", "end")
        text = text[:-1]
        file_name = self.note_file_name

        if file_name is None:
            file_name = f"Note_{int(time())}"

        if self.note_text != text:
            if not os.path.isdir(self.notes_dir):
                os.mkdir(self.notes_dir)

            with open(os.path.join(self.notes_dir, file_name), 'w') as note:
                note.write(text)

    def show_previous(self):
        notes = self.list_notes()
        
        if self.note_file_name not in notes:
            # This is a new note. Should be saved first
            self.save_note()

        notes = self.list_notes()

        if len(notes) > 0:
            try:
                note_index = notes.index(self.note_file_name) - 1
                if note_index < 0:
                    note_index = 0
            except ValueError:
                note_index = 0

            self.note_file_name = notes[note_index]
        else:
            self.note_file_name = None

        self.read_note(self.note_file_name)

    def show_next(self):
        notes = self.list_notes()

        if self.note_file_name not in notes:
            # This is a new note. Should be saved first
            self.save_note()

        notes = self.list_notes()

        if len(notes) > 0:
            try:
                note_index = notes.index(self.note_file_name) + 1
                if note_index >= len(notes):
                    note_index = len(notes) - 1
            except ValueError:
                note_index = len(notes) - 1

            self.note_file_name = notes[note_index]
        else:
            self.note_file_name = None

        self.read_note(self.note_file_name)

    def dismiss(self):
        self.save_note()
        self.save_cfg()
        self.wm_withdraw()
        self.destroy()

    def select_notes_dir(self):
        filename = filedialog.askdirectory()
        if len(filename) > 0 and os.path.isdir(filename):
            self.notes_dir = filename

    def save_cfg(self):
        if not os.path.isdir(cfg_dir):
            os.mkdir(cfg_dir)

        with open(cfg_path, 'w') as config:
            data = {
                "notes_dir": self.notes_dir,
                "x": self.winfo_x(),
                "y": self.winfo_y(),
                "current_note": self.note_file_name
            }
            config.write(json.dumps(data))

    def read_cfg(self):
        if not os.path.isdir(cfg_dir):
            os.mkdir(cfg_dir)

        if not os.path.isfile(cfg_path):
            with open(cfg_path, 'w') as config:
                data = {
                    "notes_dir": self.notes_dir,
                    "x": self.winfo_x(),
                    "y": self.winfo_y(),
                    "current_note": self.note_file_name
                }
                config.write(json.dumps(data))

        with open(cfg_path, 'r') as config:
            data = json.loads(config.read())
            self.notes_dir = data.get("notes_dir", self.notes_dir)
            x = data.get("x", self.x)
            y = data.get("y", self.y)
            self.note_file_name = data.get("current_note", None)

            max_x = self.winfo_screenwidth() - 300
            max_y = self.winfo_screenheight() - 300

            if x > max_x:
                x = max_x
            if y > max_y:
                y = max_y

            self.geometry(f"+{x}+{y}")


if __name__ == '__main__':
    main_app = MainWindow()
    main_app.mainloop()
