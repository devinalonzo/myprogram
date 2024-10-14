import tkinter as tk
from tkinter import Button
from PIL import Image, ImageTk
import os
import subprocess
import sys
import datetime

# Paths for temp directory when running from the EXE
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Paths inside the temp directory
PROGRAMS_PATH = os.path.join(base_path, "subprograms")
BACKGROUND_PATH = os.path.join(base_path, "bkgd.png")
ICON_PATH = os.path.join(base_path, "ico.png")
LOG_FILE_PATH = "C:\\DevinsProgramLog.txt"

CURRENT_VERSION = "1.0.2"  # Adjust this as needed

def log_event(event_message):
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{datetime.datetime.now()}: {event_message}\n")

def open_program(program_name):
    try:
        program_path = os.path.join(PROGRAMS_PATH, program_name)
        log_event(f"Attempting to open: {program_path}")
        if os.path.exists(program_path):
            subprocess.Popen([program_path], shell=True)
            log_event(f"Successfully opened: {program_path}")
        else:
            log_event(f"Failed to open: {program_path} (File not found)")
    except Exception as e:
        log_event(f"Error opening {program_name}: {str(e)}")

def open_anydesk():
    # Implement AnyDesk check or download
    pass

def check_for_update():
    # Implement version check and download logic
    pass

# Program selection UI
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")

    # Set the window icon using the .png file
    try:
        icon_image = ImageTk.PhotoImage(file=ICON_PATH)
        root.iconphoto(True, icon_image)
    except Exception as e:
        log_event(f"Failed to load icon: {str(e)}")

    # Group programs by their category prefix
    pump_programs = []
    crind_programs = []
    veeder_root_programs = []
    passport_programs = []
    help_resources = []

    # List programs from the local directory or EXE-bundled folder
    if os.path.exists(PROGRAMS_PATH):
        programs = os.listdir(PROGRAMS_PATH)
        for program_name in programs:
            if program_name.startswith('1-'):
                pump_programs.append(program_name)
            elif program_name.startswith('2-'):
                crind_programs.append(program_name)
            elif program_name.startswith('3-'):
                veeder_root_programs.append(program_name)
            elif program_name.startswith('4-'):
                passport_programs.append(program_name)
            elif program_name.startswith('5-'):
                help_resources.append(program_name)

    # Calculate necessary window size based on the number of programs
    max_rows = max(len(pump_programs), len(crind_programs), len(veeder_root_programs), len(passport_programs), 8)
    window_height = 700 + (max_rows * 40)
    window_width = 900
    root.geometry(f"{window_width}x{window_height}")
    root.minsize(window_width, window_height)

    # Load and set background image
    try:
        background_image = Image.open(BACKGROUND_PATH)
        background_image = background_image.resize((window_width, window_height), Image.LANCZOS)
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(root, image=background_photo)
        background_label.place(relwidth=1, relheight=1)
    except Exception as e:
        log_event(f"Failed to load background: {str(e)}")

    # Button styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")

    # Create labels for the columns
    columns = [
        ("Pump", pump_programs, 50),
        ("CRIND", crind_programs, 250),
        ("Veeder-Root", veeder_root_programs, 450),
        ("Passport", passport_programs, 650)
    ]

    # Place programs into their respective columns and make buttons resizable
    for column_name, column_programs, column_x in columns:
        column_label = tk.Label(root, text=column_name, bg=button_bg, fg=button_fg, font=button_font)
        column_label.place(x=column_x, y=20)
        for idx, program_name in enumerate(column_programs[:8]):  # Limit each column to 8 programs
            program_display_name = os.path.splitext(program_name)[0][2:]  # Remove prefix
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=column_x, y=60 + idx * 40)

    # Add Help/Resources section at the bottom, centered vertically
    help_label = tk.Label(root, text="Help/Resources", bg=button_bg, fg=button_fg, font=button_font)
    help_label.place(x=50, y=window_height - 200)  # Adjusted position
    for idx, program_name in enumerate(help_resources):
        program_display_name = os.path.splitext(program_name)[0][2:]  # Remove 'h-' prefix
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                        command=lambda name=program_name: open_program(name))
        button.place(x=50 + idx * 150, y=window_height - 160)

    # Add AnyDesk and Update buttons
    anydesk_button = Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font,
                            command=open_anydesk)
    anydesk_button.place(x=650, y=window_height - 200)

    update_button = Button(root, text="Check for Update", bg=button_bg, fg=button_fg, font=button_font,
                           command=check_for_update)
    update_button.place(x=650, y=window_height - 160)

    # Display version number in the bottom-right corner
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    root.mainloop()

# Run the program selection interface
program_selection()
