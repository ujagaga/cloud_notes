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
from tkinter import Tk, Button, Frame, LEFT, RIGHT, X, Y, TOP, BOTTOM, BOTH, Text, filedialog, YES, NO, \
    Scrollbar, Listbox, END, NW, PhotoImage
import os
import json
from time import time
import tempfile
from signal import SIGINT
import base64


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

IMG_BTN_DELETE = (
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAA7EAA"
    "AOxAGVKw4bAAACZklEQVRIie2VP2gaURzHf6d3nqeFBKtQqdLFeEVMLQ1C8M/g"
    "1qKLhf6hkIQOzllipoaM0kFBLIXOKXTIkG6thcShiBZvTCmiPQUTjiaKIR4x6V"
    "3u1+mCpkZraZaSH7zhfd7j+/m9x4NHwIDa2Ni4m0qlMoeHh35FUYhBe9SiaRqm"
    "pqY+plKpeavVun9+nTwPEJEMBALv8/n8LZvNBgaDYVg+CIIAHMfdl2X5NQA8Gr"
    "oZAIDneY/RaES3291pNps3EZEeNgqFwgOGYdDr9R4MyvvtBCcnJ4osy6DX6w/M"
    "ZvPuqIaOjo6+0jQNsiwPvEoiHA5/7na7k2dGktRvbm46LBaL5HK5yqMEFEXpcr"
    "mcc2Ji4nR6evpb75rdbi8DwzAIAJcyWJb9SWxtbflFUTSP6vRvymaz1fvA2tra"
    "vXQ6He1lpVKJXV1dfYiIjMp2dnaur6ysPNvb27umMkTUZTKZJ9vb2zcuNPr9ft"
    "5kMmG1WnWoLBwOf9BoNLi+vv5UZQsLCy8BABcXF1+oLJlMzhMEgdFo9G1vpqZ3"
    "cnx8THe7XUBEncpEUdQqigK1Wu1UZZ1ORwcA0Gq1zl6hIAg0IgLHcT8uFFxGXQ"
    "muBP+DwOv1FoPBoDA7O1vuYZzP59v3eDylsWwzMzO7DMNgpVJxjdvp0tJSDADQ"
    "brcne/k/vyKtVtuX2fejURSFkiRBuVy+U6lUvv9pqMPh0Mbj8dsAACzLWuv1+m"
    "CB0+n8VCwWn8/Nzb2zWCxjdd5oNIAkSYhEIl+y2ewZ7/tH2+32ZCwWe8Xz/GNJ"
    "kqhxBAaDQQyFQm8SicQyQRCKyn8BAEkQk60EBxsAAAAASUVORK5CYII="
)

IMG_BTN_BROWSE = (
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAA"
    "ALEwEAmpwYAAABqElEQVRIia3WsWsUURDH8c8ZOYN/gI2tpUUQESuTUoiNNnKY"
    "IoWgf4AQUop/gJWFhWChiZWCtSDYCykUTHVCAkKUKCZp4iVr8Wa5Tdhd9+X8we"
    "O43Zn5zrx5N+9ImscaDlA0rB08xCmZmscIh/iGYc3aqoBeoZ8DWIvgd1tszkoV"
    "lJA3ON0VcBCZ/0tDR7fspY6VFOGcCyjwWodKJgEUeP6/AF8aAAVuNjl1bhTu4H"
    "Llex8LuIJrUuMnAnyMVdV3rLbFyQHU6R2u43ebUdcenEjZP/vQjLQ1G9I2vccA"
    "vTrj3AoWsR8+j/EIHyLOCqYmAcxE8BVM14BHWJ4EsBq2x4OXeoptx0ZIDmBD2p"
    "YmzUa8S+WD3CZPY7fl/V58njkp4JOUZZPmpD6sVx/mbNEg7Bdr3l3AD+lCOqJD"
    "bHYE9KQTNJIaOivNpwcRvJyuV6tOnwNyqyNkSjqK28bT9E9k/tb4/p4rM7odWZ"
    "FG8n5L8CHuS3d0Hxelhq4HcIAXUm/3cKN0XMDXqKRp5pdrC0s435DEPeN/Jz+r"
    "s6OHc7pP2F/Gx7IO8gTP/gIHVZWZJsDEggAAAABJRU5ErkJggg=="
)

IMG_BTN_NEW = (
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAaCAYAAACtv5zzAAAACXBIWXMAAAsTAA"
    "ALEwEAmpwYAAACL0lEQVRIibXWy29NURQG8B+ttloh0lLREEoTCQMSaSvVSKgU"
    "IyTERJB4DAz4GwyYmNYAAxLVqMTEQGJiItGJqyIx8EiuotHoQBviXQZ7nzi9bq"
    "/b01jJytmPb6/vrL3WXnsTZAX6MI5f/9CHaDcNWYl3ZRhO62fsLZfgZlz0Elux"
    "dAptwu0UyXccKofgY1zQXQb2dIEn37C/1ILZqIvtl2UQ/Czoz0EvTpQimKlUog"
    "dH/hcBVOAidhZjnySdnZ0dQ0ND69Nj9fX173O5XD8+lCCpxAWswkR6IgnYamhs"
    "bBxUkJbV1dUTvb29CwWPu7E7pftwNYWfmzY+Kw5CC150dXVtyOfz69KghoaG0Y"
    "GBgTsl/r4Jb2K7VjgnxT3IKPNxNuqkbf8rBriBjikMjaANP1JjVWjFK4xhMYaT"
    "yWJZNIK3JfRXCnsAOaFs1GANbuES5iWgrFt0FHdRj2Yh0D1CXE/innAQMxE04k"
    "nqL1ujjdEU5hxOFYtBOZKkZoeQli1xvEpIXbiGK2TzoAfb8drUJX0HnmX14JOw"
    "PYNCxtRhrZBduYgZT8BZPNiFy6l+sRi0CxmViaACD7BlCoLaON+WlYBwjz8WUr"
    "I5fo9hUzR+PAHOpFQswBk8wtOo/diYBo1Fgj0ZCBJZjm3YXDhRKQTisJB6NXgx"
    "TeMrcR7LhDp2vxCwBM9N79lSTPORZJJUCK+KPuEULopeffXnrpgQnijJhT8h1P"
    "svETeM6zgoVUUT+Q1NqsPV30TQYwAAAABJRU5ErkJggg=="
)

IMG_BTN_NEXT = (
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAPCAYAAAD+pA/bAAAACXBIWXMAAA7EAA"
    "AOxAGVKw4bAAABZklEQVQ4jWNgIAFERUUJSklJ7WRjY/svICDwTkdHJ2/VqlXM"
    "pJiBF0hLS09nYGD4j4zFxMSOeHt7a1LFAjExsfPoFjAwMPxnZ2f/rqGhUblt2z"
    "Z2dD2MDAwMDGlpafwPHz7UY2JiYsJnwdmzZ+e/evVKEZe8sLDwOQsLi7StW7ee"
    "hQva29v7cnFxfcTmMnIwKyvrTw0NjfZJkyZBfCMiIvKQWoYjY0FBwatubm46jO"
    "zs7P9//vyJL2TIBtLS0lcY2djY/v/69YsmFvDy8jIQileKACcn53Embm7u27Qw"
    "XERE5KS9vX0cg5WVlR0vL+9LBipFLjs7+1cdHZ3SM2fOsDIwQPPBpEmT2Ddv3i"
    "xHKLJv3Lix5dWrV2q45CUlJQ+Zmpomb9q06Q653j6DzdVcXFwfDQwMsurr6ymL"
    "UBUVlSnohktLS2/z9/eXpchgGJg0aRKfkpLSWkFBwR+CgoL3rKysEgnpAQC8O6"
    "WuApdWSQAAAABJRU5ErkJggg=="
)

IMG_BTN_PREV = (
    "iVBORw0KGgoAAAANSUhEUgAAABgAAAAPCAYAAAD+pA/bAAAACXBIWXMAAA7EAA"
    "AOxAGVKw4bAAAA50lEQVQ4jbXUsUoDQRSF4W9jSCOmSRGEQBpbwdoypVUa09ik"
    "svcFLH0DC2vxCWwstBPFRl8gYKlNwEBALXQtNgthkzibZPfAKQbu/e+dwzCEdY"
    "RXfOEKmzl6cqmFa/winvLZuuAKjvGRAae+WwZWzZx3cIHOPz1b2A1wYwwksYIN"
    "nGC8YOtV/I59aOOhQPC0n0kyLQMe4zPCCPVApqvqu4L7kuAkT1wTN8qJ6CmdFK"
    "GPYYHwAfaizJW2cY7uZOg8PaIXiCZ9pj+LCg4nBfM2uw3Ac6uBS7N/0WlRA1Id"
    "4AVvkvhqyzT/AdrnmE4cwsQgAAAAAElFTkSuQmCC"
)


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
        self.notes = []
        self.note_listbox = None
        self.scrollbar = None

        self.notes_dir = default_notes_dir
        self.note_file_name = None

        self.show_note_list_flag = True
        self.note_text = ""

        self.frame_browser = Frame(self, bg=COLOR_BACKGROUND)
        self.frame_browser.pack(fill=BOTH, side=LEFT, expand=NO)

        self.frame_note_editor = Frame(self, bg=COLOR_BACKGROUND)
        self.frame_note_editor.pack(fill=X, side=RIGHT, expand=YES)

        self.frame_note_list = Frame(self.frame_browser, bg=COLOR_BACKGROUND, width=200)
        self.frame_note_list.pack(fill=BOTH, side=LEFT)

        self.browse_image = PhotoImage(data=IMG_BTN_BROWSE)
        self.btn_browse = Button(self.frame_note_list, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, image=self.browse_image,
                                 command=self.select_notes_dir, width=26, height=26, borderwidth=0)
        self.btn_browse.pack(side=TOP, anchor=NW)

        self.scrollbar = Scrollbar(self.frame_note_list)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.note_listbox = Listbox(self.frame_note_list, bg=COLOR_BACKGROUND, fg=COLOR_TEXT)
        self.note_listbox.pack(side=LEFT, fill=Y)
        self.note_listbox.bind("<<ListboxSelect>>", self.file_selected)

        self.note_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.note_listbox.yview)

        self.btn_show_list = Button(self.frame_browser, text=">", bg=COLOR_BACKGROUND, fg=COLOR_TEXT,
                                    width=1, padx=0, borderwidth=0)
        self.btn_show_list.pack(side=RIGHT, fill=Y)
        self.btn_show_list.bind('<Button-1>', self.show_hide_note_list)
        self.btn_show_list.bind('<ButtonRelease-1>', self.fix_offset)

        self.frame_btn = Frame(self.frame_note_editor, bg=COLOR_BACKGROUND)
        self.frame_btn.pack(fill=X, side=TOP)

        self.prev_btn_image = PhotoImage(data=IMG_BTN_PREV)
        self.btn_prev = Button(self.frame_btn, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, image=self.prev_btn_image,
                               command=self.show_previous, width=26, height=26, pady=0, borderwidth=0)
        self.btn_prev.pack(side=LEFT)

        self.next_btn_image = PhotoImage(data=IMG_BTN_NEXT)
        self.btn_next = Button(self.frame_btn, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, image=self.next_btn_image,
                               command=self.show_next, width=26, height=26, pady=0, borderwidth=0)
        self.btn_next.pack(side=LEFT)

        self.new_note_image = PhotoImage(data=IMG_BTN_NEW)
        self.btn_new = Button(self.frame_btn, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, image=self.new_note_image,
                              command=self.new_note, width=26, height=26, borderwidth=0)
        self.btn_new.pack(side=LEFT)

        self.del_image = PhotoImage(data=IMG_BTN_DELETE)
        self.btn_delete = Button(self.frame_btn, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, image=self.del_image,
                                 command=self.delete_note, width=26, height=26, pady=0, borderwidth=0)
        self.btn_delete.pack(side=LEFT)

        self.display_text = Text(self.frame_note_editor, bg=COLOR_BACKGROUND, fg=COLOR_TEXT, borderwidth=0, padx=5, pady=5,
                                 undo=True, autoseparators=True, maxundo=1, spacing1=5, spacing2=0, spacing3=5)
        self.display_text.pack(padx=0, pady=0, fill=BOTH, expand=True)
        self.display_text.bind("<<Paste>>", self.custom_paste)

        self.read_cfg()
        self.read_note()

        self.focus_force()

    def refresh_note_list(self):
        self.list_notes()

        self.note_listbox.delete(0, END)
        for note in self.notes:
            self.note_listbox.insert(END, note)

        if self.note_file_name in self.notes:
            note_index = self.notes.index(self.note_file_name)
            self.note_listbox.select_set(note_index)

    def file_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.note_file_name = event.widget.get(index)

            self.save_note()
            self.read_note()

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

        self.note_text = ""
        self.note_file_name = f"Note_{int(time())}"
        self.display_text.delete(1.0, END)
        self.set_title("New")
        self.refresh_note_list()

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

        self.read_note()

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

    def read_note(self):
        self.display_text.delete(1.0, END)
        self.list_notes()

        if self.note_file_name is None:
            # No Note set. Set first one if exists
            if len(self.notes) > 0:
                self.note_file_name = self.notes[0]
            else:
                # No notes available
                self.note_file_name = f"Note_{int(time())}"

        note_index = "New"
        try:
            if self.note_file_name is not None:
                with open(os.path.join(self.notes_dir, self.note_file_name), 'r') as note:
                    self.note_text = note.read()
                    self.display_text.insert(1.0, self.note_text)
                    note_index = f"{self.notes.index(self.note_file_name) + 1}/{len(self.notes)}"
        except FileNotFoundError:
            # This note no longer exists. Remove from config.
            self.note_file_name = None
            self.save_cfg()
            self.note_file_name = f"Note_{int(time())}"

        self.set_title(note_index)
        self.refresh_note_list()

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

        self.read_note()

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

        self.read_note()

    def dismiss(self):
        self.save_note()
        self.save_cfg()
        self.wm_withdraw()
        self.destroy()

    def select_notes_dir(self):
        filename = filedialog.askdirectory()
        if len(filename) > 0 and os.path.isdir(filename):
            self.notes_dir = filename
            self.list_notes()
            self.note_file_name = None
            if len(self.notes) > 0:
                self.note_file_name = self.notes[0]

            self.read_note()

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
        if not os.path.isfile(cfg_path):
            self.save_cfg()

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

        self.refresh_note_list()


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
