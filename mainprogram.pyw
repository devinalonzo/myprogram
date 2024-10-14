import os
import sys
import tkinter as tk
from tkinter import Button, Label
from PIL import Image, ImageTk
import subprocess
import logging

# Constants for paths
CURRENT_VERSION = "1.0.2"  # Set your current version here
LOG_PATH = "C:/DevinsProgramLog.txt"
TEMP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
PROGRAMS_PATH = os.path.join(TEMP_DIR, 'subprograms')
ICON_PATH = os.path.join(TEMP_DIR, 'ico.png')
BACKGROUND_PATH = os.path.join(TEMP_DIR, 'bkgd.png')

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s - %(message)s')
logging.info("Program started.")

# Function to open programs
def open_program(program_name):
    try:
        program_path = os.path.join(PROGRAMS_PATH, program_name)
        subprocess.Popen([program_path], shell=True)
        logging.info(f"Opened program: {program_name}")
    except Exception as e:
        logging.error(f"Failed to open {program_name}: {str(e)}")

# Function to open AnyDesk
def open_anydesk():
    try:
        anydesk_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'AnyDesk.exe')
        if not os.path.exists(anydesk_path):
            # Download AnyDesk if not found
            logging.info("AnyDesk not found. Downloading...")
            # Download logic here
        subprocess.Popen([anydesk_path], shell=True)
        logging.info("Opened AnyDesk.")
    except Exception as e:
        logging.error(f"Failed to open AnyDesk: {str(e)}")

# Function to check for update
def check_for_update():
    # Your update checking logic comparing current build with GitHub release
    try:
        logging.info("Checking for updates...")
        # Check update logic here
    except Exception as e:
        logging.error(f"Failed to check for updates: {str(e)}")

# UI layout
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")
    root.geometry("1200x600")

    # Set the window icon
    icon_image = ImageTk.PhotoImage(file=ICON_PATH)
    root.iconphoto(True, icon_image)

    # Load background image
    background_image = Image.open(BACKGROUND_PATH)
    background_image = background_image.resize((1200, 600), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Button and label styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")
    label_font = ("Helvetica", 14, "bold")
    
    # Define columns and buttons
    columns = [
        ("Pump", 60, 140, []),
        ("CRIND", 380, 140, []),
        ("Veeder-Root", 700, 140, []),
        ("Passport", 1020, 140, [])
    ]

    help_resources = []

    # List programs from the directory
    if os.path.exists(PROGRAMS_PATH):
        programs = os.listdir(PROGRAMS_PATH)
        for program_name in programs:
            if program_name.startswith('1-'):
                columns[0][3].append(program_name)
            elif program_name.startswith('2-'):
                columns[1][3].append(program_name)
            elif program_name.startswith('3-'):
                columns[2][3].append(program_name)
            elif program_name.startswith('4-'):
                columns[3][3].append(program_name)
            elif program_name.startswith('5-'):
                help_resources.append(program_name)

    # Place program buttons in respective columns
    for column_name, column_x, start_y, program_list in columns:
        column_label = Label(root, text=column_name, bg=button_bg, fg=button_fg, font=label_font)
        column_label.place(x=column_x, y=start_y - 60)
        for idx, program_name in enumerate(program_list):
            program_display_name = os.path.splitext(program_name)[0][2:]  # Strip the first two characters for display
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=column_x, y=start_y + idx * 60)

    # Help/Resources buttons layout
    help_start_x = 60
    help_start_y = 400
    for idx, program_name in enumerate(help_resources):
        program_display_name = os.path.splitext(program_name)[0][2:]
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                        command=lambda name=program_name: open_program(name))
        button.place(x=help_start_x + (idx % 2) * 320, y=help_start_y + (idx // 2) * 60)

    # Add AnyDesk and Update buttons
    update_button = Button(root, text="Check for Update", bg=button_bg, fg=button_fg, font=button_font,
                           command=check_for_update)
    update_button.place(x=1020, y=460)

    anydesk_button = Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font,
                            command=open_anydesk)
    anydesk_button.place(x=900, y=460)

    # Display version number in the bottom-right corner
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(x=1020, y=520)

    root.mainloop()

# Run the program selection UI
if __name__ == "__main__":
    program_selection()
