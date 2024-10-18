import os
import tkinter as tk
from tkinter import Button, messagebox
from PIL import Image, ImageTk
import subprocess
import logging
import sys
import shutil

# Function to get the path from the temporary folder (_MEIPASS)
def get_temp_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return os.path.join(os.getcwd(), filename)

# Define paths using the temp folder mechanism
ICON_PATH = get_temp_path('ico.png')
BACKGROUND_PATH = get_temp_path('bkgd.png')
PROGRAMS_PATH = get_temp_path('subprograms')  # Directory with subprogram EXEs
VERSION_FILE_PATH = get_temp_path('version.txt')
LOG_FILE_PATH = 'C:\\DevinsFolder\\mainprogram.log'

# Unpack files from the temporary directory (sys._MEIPASS)
def unpack_files():
    try:
        if hasattr(sys, '_MEIPASS'):
            # Files are already extracted to the temp directory, no need to manually unpack
            temp_dir = sys._MEIPASS
            logging.info(f"Files already available in temporary directory: {temp_dir}")
    except Exception as e:
        logging.error(f"Error accessing files in temp directory: {e}")
        messagebox.showerror("Error", f"Error accessing files in temp directory. {e}")

# Set up logging
def setup_logging():
    os.makedirs('C:\\DevinsFolder', exist_ok=True)
    logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Copy version file from temp to a writable directory (optional)
def setup_version_file():
    try:
        temp_version_path = get_temp_path('version.txt')
        shutil.copy(temp_version_path, 'C:\\DevinsFolder\\version.txt')
    except Exception as e:
        logging.error(f"Error copying version.txt: {e}")
        messagebox.showerror("Error", f"Error copying version.txt: {e}")

# Function to read version number
def read_version():
    try:
        if os.path.exists(VERSION_FILE_PATH):
            with open(VERSION_FILE_PATH, 'r') as version_file:
                return version_file.read().strip()
        else:
            logging.error(f"version.txt not found in {VERSION_FILE_PATH}")
            return "BETA"
    except Exception as e:
        logging.error(f"Error reading version file: {e}")
        return "BETA"

logging.info(f"Starting Devin's Program")

# Function to open a subprogram
def open_program(program_name):
    try:
        program_path = os.path.join(PROGRAMS_PATH, program_name)
        if os.path.exists(program_path):
            subprocess.Popen([program_path], shell=True)
            logging.info(f"Opened program: {program_path}")
        else:
            logging.error(f"Program not found: {program_path}")
            messagebox.showerror("Error", f"Program not found: {program_name}")
    except Exception as e:
        logging.error(f"Error opening program: {e}")

# Function to open AnyDesk
def open_anydesk():
    try:
        anydesk_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'AnyDesk.exe')
        if os.path.exists(anydesk_path):
            subprocess.Popen([anydesk_path], shell=True)
        else:
            logging.info("AnyDesk not found, downloading...")
            url = "https://download.anydesk.com/AnyDesk.exe"
            download_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'AnyDesk.exe')
            subprocess.run(['curl', '-o', download_path, url])
            subprocess.Popen([download_path], shell=True)
    except Exception as e:
        logging.error(f"Error opening AnyDesk: {e}")

# Function to check for updates
def check_for_update():
    try:
        import requests
        release_url = "https://api.github.com/repos/devinalonzo/myprogram/releases/latest"
        response = requests.get(release_url)
        latest_version = response.json()['tag_name'].strip()

        if CURRENT_VERSION >= latest_version:
            messagebox.showinfo("Update", "You have the latest version!")
        else:
            messagebox.showinfo("Update", f"New version available: {latest_version}")
            update_url = response.json()['assets'][0]['browser_download_url']
            download_path = os.path.join(os.path.expanduser('~'), 'Desktop', f'DevinsProgram_{latest_version}.exe')
            subprocess.run(['curl', '-L', '-o', download_path, update_url])
            messagebox.showinfo("Update", f"Downloaded update to {download_path}")
        logging.info(f"Update checked: Current version {CURRENT_VERSION}, Latest version {latest_version}")
    except Exception as e:
        logging.error(f"Error checking for update: {e}")
        messagebox.showerror("Error", "Could not check for updates")

# Program selection UI
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")

    # Set the window icon using the .png file
    try:
        icon_image = ImageTk.PhotoImage(file=ICON_PATH)
        root.iconphoto(True, icon_image)
    except FileNotFoundError:
        logging.error(f"Icon file not found: {ICON_PATH}")
        messagebox.showerror("Error", f"Icon file not found: {ICON_PATH}")

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

    # Set up window size and background
    root.geometry("1200x600")
    root.minsize(1200, 600)  # Set a minimum size for the window

    # Load and set background image
    try:
        background_image = Image.open(BACKGROUND_PATH)
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(root, image=background_photo)
        background_label.place(relwidth=1, relheight=1)
    except FileNotFoundError:
        logging.error(f"Background image not found: {BACKGROUND_PATH}")
        messagebox.showerror("Error", f"Background image not found: {BACKGROUND_PATH}")

    # Button styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")

    # Layout rules
    start_x = 60
    start_y = 140
    button_gap_x = 320
    button_gap_y = 60

    # Create labels for the columns
    columns = [
        ("Pump", pump_programs, start_x),
        ("CRIND", crind_programs, start_x + button_gap_x),
        ("Veeder-Root", veeder_root_programs, start_x + 2 * button_gap_x),
        ("Passport", passport_programs, start_x + 3 * button_gap_x)
    ]

    # Place programs into their respective columns and make buttons resizable
    for column_name, column_programs, column_x in columns:
        column_label = tk.Label(root, text=column_name, bg=button_bg, fg=button_fg, font=button_font)
        column_label.place(x=column_x, y=start_y - 60)
        for idx, program_name in enumerate(column_programs[:8]):  # Limit each column to 8 programs
            program_display_name = os.path.splitext(program_name)[0][2:]  # Remove prefix (1-, 2-, etc.)
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=column_x, y=start_y + idx * button_gap_y)

    # Add Help/Resources section at the bottom
    help_label = tk.Label(root, text="Help/Resources", bg=button_bg, fg=button_fg, font=button_font)
    help_label.place(x=start_x, y=400 - 60)
    for idx, program_name in enumerate(help_resources):
        program_display_name = os.path.splitext(program_name)[0][2:]  # Remove '5-' prefix
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                        command=lambda name=program_name: open_program(name))
        button.place(x=start_x + (idx // 3) * 150, y=400 + (idx % 3) * 60)

    # Add AnyDesk and Update buttons
    update_button = Button(root, text="Check for Update", bg=button_bg, fg=button_fg, font=button_font,
                           command=check_for_update)
    update_button.place(x=start_x + 3 * button_gap_x, y=460)

    anydesk_button = Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font,
                            command=open_anydesk)
    anydesk_button.place(x=start_x + 3 * button_gap_x - 120, y=460)

    # Display version number in the bottom-right corner
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(x=start_x + 3 * button_gap_x, y=520)

    root.mainloop()

# Set up the program
unpack_files()  # Unpack necessary files
setup_logging()  # Set up logging after file unpacking
setup_version_file()  # Copy version.txt to a writable location

# Read the version number
CURRENT_VERSION = read_version()

# Start the program
if __name__ == "__main__":
    program_selection()
