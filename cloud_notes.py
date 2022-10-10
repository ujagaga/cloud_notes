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
from tkinter import Tk, Button, Frame, LEFT, RIGHT, X, Y, TOP, BOTH, Text, filedialog, YES, NO, Scrollbar, Listbox, END
import os
import json
from time import time
import tempfile
from signal import SIGINT

COLOR_BACKGROUND = "#ffebb8"
COLOR_TEXT = "#21130d"

APP_TITLE = "Cloud Notes"
MAX_FILE_SIZE = 1024        # If the file is bigger than 1Mb, it will not be opened to prevent app from freezing
FILE_LIST_WIDTH = 100

cfg_name = "settings.cfg"
user_dir = os.path.expanduser("~")
cfg_dir = os.path.join(user_dir, ".cloud_notes")
cfg_path = os.path.join(cfg_dir, cfg_name)
default_notes_dir = os.path.join(cfg_dir, "notes")


class MainWindow(Tk):
    """
    Main TK inter window definition
    """
    def __init__(self):
        Tk.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.dismiss)

        self.title(APP_TITLE)
        self.minsize(300, 300)
        self.configure(background=COLOR_BACKGROUND)

        self.x = 200
        self.y = 200
        self.width = 300
        self.height = 300
        self.offset_x = 6
        self.offset_y = 29
        self.notes =[]
        self.note_listbox = None
        self.scrollbar = None

        self.notes_dir = default_notes_dir
        self.note_file_name = None

        self.show_note_list_flag = True
        self.note_text = ""

        self.frame_browser = Frame(self, bg=COLOR_BACKGROUND)
        self.frame_browser.pack(fill=BOTH, side=LEFT, expand=NO)

        self.frame_notes = Frame(self, bg=COLOR_BACKGROUND)
        self.frame_notes.pack(fill=X, side=RIGHT, expand=YES)

        self.frame_note_list = Frame(self.frame_browser, bg=COLOR_BACKGROUND, width=200)
        self.frame_note_list.pack(fill=BOTH, side=LEFT)

        self.scrollbar = Scrollbar(self.frame_note_list)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.note_listbox = Listbox(self.frame_note_list, bg=COLOR_BACKGROUND, fg=COLOR_TEXT)
        self.note_listbox.pack(side=LEFT, fill=Y)
        self.note_listbox.bind("<<ListboxSelect>>", self.file_selected)

        self.btn_show_list = Button(self.frame_browser, text=">", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                                    width=1, pady=0, borderwidth=0)
        self.btn_show_list.pack(side=RIGHT, fill=Y)
        self.btn_show_list.bind('<Button-1>', self.show_hide_note_list)
        self.btn_show_list.bind('<ButtonRelease-1>', self.fix_offset)

        self.frame_btn = Frame(self.frame_notes, bg=COLOR_BACKGROUND)
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

        self.display_text = Text(self.frame_notes, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, borderwidth=0, padx=5, pady=5,
                                 undo=True, autoseparators=True, maxundo=1, spacing1=5, spacing2=0, spacing3=5)
        self.display_text.pack(padx=0, pady=0, fill=BOTH, expand=True)
        self.display_text.bind("<<Paste>>", self.custom_paste)

        self.read_cfg()
        self.read_note(self.note_file_name)

        self.update_note_list()
        self.focus_force()

    def file_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            file_name = event.widget.get(index)

            self.save_note()
            self.list_notes()
            self.update_note_list()
            self.note_listbox.select_set(index)

            self.read_note(file_name)

    def fix_offset(self, event):
        self.offset_x = self.winfo_x() - self.x
        self.offset_y = self.winfo_y() - self.y

    def show_hide_note_list(self, event):
        self.y = self.winfo_y() - self.offset_y
        self.x = self.winfo_x() - self.offset_x
        self.width = self.winfo_width()
        self.height = self.winfo_height()

        if self.show_note_list_flag:
            self.show_note_list_flag = False
            list_width = -self.frame_note_list.winfo_width()
            self.frame_note_list.pack_forget()
            self.btn_show_list.config(text="<")
        else:
            self.show_note_list_flag = True
            self.frame_note_list.pack(side=RIGHT, fill=Y)
            self.btn_show_list.config(text=">")
            list_width = self.frame_note_list.winfo_width()

        self.width += list_width
        self.x -= list_width
        self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def update_note_list(self):
        self.note_listbox.delete(0, END)
        for note in self.notes:
            self.note_listbox.insert(END, note)

        self.note_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.note_listbox.yview)

    def set_title(self, new_title):
        """
        Sets the main window title
        :param new_title: The new string to append to the application main title
        """
        self.title(f"{APP_TITLE} - {new_title}")

    def custom_paste(self, event):
        """
        By default, the Text widget will perform an insert, ignoring the selected content.
        This function deletes the selected content so we can paste over selected.
        :param event: Detected event
        :return: "break" message to TK Inter
        """
        try:
            event.widget.delete("sel.first", "sel.last")
        except:
            pass
        event.widget.insert("insert", event.widget.clipboard_get())
        return "break"
        
    def new_note(self):
        """
        Prepares the app for writing a new note
        """
        self.save_note()
        self.list_notes()
        self.update_note_list()

        self.note_text = ""
        self.note_file_name = f"Note_{int(time())}"
        self.display_text.delete(1.0, END)
        self.set_title("New")

    def delete_note(self):
        """
        Removes the current note from the file system and the Text widget.
        After this it moves on to the previous one.
        """
        self.display_text.delete(1.0, END)
        self.note_text = ""

        full_path = os.path.join(self.notes_dir, self.note_file_name)
        self.list_notes()

        note_index = len(self.notes) - 1
        if len(self.notes) > 0:
            try:
                note_index = self.notes.index(self.note_file_name)
            except ValueError:
                note_index = len(self.notes) - 1

        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"ERROR: Could not remove file {full_path}. {e}")

        self.list_notes()

        if note_index < len(self.notes):
            self.note_file_name = self.notes[note_index]
        elif len(self.notes) == 0:
            self.note_file_name = f"Note_{int(time())}"
        else:
            note_index = len(self.notes) - 1
            self.note_file_name = self.notes[note_index]

        self.read_note(self.note_file_name)
        self.update_note_list()
        if note_index >= 0:
            self.note_listbox.selection_clear(0, END)
            self.note_listbox.select_set(note_index)

    def list_notes(self):
        """
        Lists all notes in the selected note folder
        :return: List of files detected, smaller than MAX_FILE_SIZE
        """
        self.notes = []

        if os.path.isdir(self.notes_dir):
            files = os.listdir(self.notes_dir)

            for file in files:
                full_path = os.path.join(self.notes_dir, file)
                if os.path.isfile(full_path):
                    file_stats = os.stat(full_path)
                    if file_stats.st_size < MAX_FILE_SIZE:
                        self.notes.append(file)

        self.notes.sort()

    def read_note(self, file_name):
        self.display_text.delete(1.0, END)
        self.list_notes()

        if file_name is None:
            # No Note set. Set first one if exists
            if len(self.notes) > 0:
                self.note_file_name = self.notes[0]
            else:
                # No notes available
                self.note_file_name = f"Note_{int(time())}"

        try:
            with open(os.path.join(self.notes_dir, file_name), 'r') as note:
                self.note_text = note.read()
                self.display_text.insert(1.0, self.note_text)
                self.note_file_name = file_name
                note_index = f"{self.notes.index(file_name) + 1}/{len(self.notes)}"
        except FileNotFoundError:
            # This note no longer exists. Remove from config.
            self.note_file_name = None
            self.save_cfg()
            self.note_file_name = f"Note_{int(time())}"
            note_index = "New"

        self.set_title(note_index)

    def save_note(self):
        text = self.display_text.get("1.0", END)
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
        self.list_notes()

        note_index = -1
        if self.note_file_name not in self.notes:
            # This is a new note. Should be saved first
            self.save_note()

        self.list_notes()

        if len(self.notes) > 0:
            try:
                note_index = self.notes.index(self.note_file_name) - 1
                if note_index < 0:
                    note_index = 0
            except ValueError:
                note_index = 0

            self.note_file_name = self.notes[note_index]
        else:
            self.note_file_name = None

        self.read_note(self.note_file_name)
        if note_index >= 0:
            self.update_note_list()
            self.note_listbox.selection_clear(0, END)
            self.note_listbox.select_set(note_index)

    def show_next(self):
        self.list_notes()

        note_index = -1
        if self.note_file_name not in self.notes:
            # This is a new note. Should be saved first
            self.save_note()

        self.list_notes()

        if len(self.notes) > 0:
            try:
                note_index = self.notes.index(self.note_file_name) + 1
                if note_index >= len(self.notes):
                    note_index = len(self.notes) - 1
            except ValueError:
                note_index = len(self.notes) - 1

            self.note_file_name = self.notes[note_index]
        else:
            self.note_file_name = None

        self.read_note(self.note_file_name)
        if note_index >= 0:
            self.update_note_list()
            self.note_listbox.selection_clear(0, END)
            self.note_listbox.select_set(note_index)

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
                "width": self.winfo_width(),
                "height": self.winfo_height(),
                "offset_x": self.offset_x,
                "offset_y": self.offset_y,
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
                    "width": self.winfo_width(),
                    "height": self.winfo_height(),
                    "offset_x": self.offset_x,
                    "offset_y": self.offset_y,
                    "current_note": self.note_file_name
                }
                config.write(json.dumps(data))

        with open(cfg_path, 'r') as config:
            data = json.loads(config.read())
            self.notes_dir = data.get("notes_dir", self.notes_dir)
            self.width = data.get("width", self.winfo_width())
            self.height = data.get("height", self.winfo_height())
            self.offset_x = data.get("offset_x", self.offset_x)
            self.offset_y = data.get("offset_y", self.offset_y)
            self.x = data.get("x", self.x) - self.offset_x
            self.y = data.get("y", self.y) - self.offset_y
            self.note_file_name = data.get("current_note", None)

            max_x = self.winfo_screenwidth() - 300
            max_y = self.winfo_screenheight() - 300

            if self.x > max_x:
                self.x = max_x
            if self.x < 0:
                self.x = 0
            if self.y > max_y:
                self.y = max_y
            if self.y < 0:
                self.y = 0

            # Set window position
            self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
            self.btn_show_list.invoke()


def ensure_single_instance():
    tmp_dir = tempfile.gettempdir()
    lock_file = os.path.join(tmp_dir, f"{APP_TITLE.replace(' ', '')}.lock")

    # Check if lock file exists and contains app PID
    old_pid = 0
    if os.path.isfile(lock_file):
        try:
            with open(lock_file, 'r') as file:
                old_pid = int(file.read())
        except:
            pass

    if old_pid != 0:
        # Check if app is running
        try:
            os.kill(old_pid, 0)
            print("ERROR: App is already running. Sending the kill signal.")
            os.kill(old_pid, SIGINT)
        except OSError:
            pass

    # Write a new PID.
    with open(lock_file, 'w') as file:
        file.write(f"{os.getpid()}")


if __name__ == '__main__':
    ensure_single_instance()
    main_app = MainWindow()

    try:
        main_app.mainloop()
    except KeyboardInterrupt:
        print("INFO: Received a keyboard interrupt event. Exiting.")
        main_app.save_cfg()
        main_app.save_note()
