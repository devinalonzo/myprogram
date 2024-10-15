import os
import sys
import subprocess
import logging
import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Define constants
STATIC_FOLDER = 'C:\\DevinsFolder'
ICON_PATH = os.path.join(STATIC_FOLDER, 'ico.png')
BACKGROUND_PATH = os.path.join(STATIC_FOLDER, 'bkgd.png')
LOG_FILE_PATH = os.path.join(STATIC_FOLDER, 'mainprogram.log')

# Ensure that C:\DevinsFolder exists
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# Set up logging in C:\DevinsFolder
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(message)s')
logging.info("Main program started")

# Function to open subprograms, passing C:\DevinsFolder as an argument
def open_program(program_name):
    try:
        program_path = os.path.join(STATIC_FOLDER, program_name)
        logging.debug(f"Attempting to open {program_name} from {program_path}")
        
        # Launch the subprogram and pass the static folder as an argument
        subprocess.Popen([program_path, STATIC_FOLDER])
    except Exception as e:
        logging.error(f"Failed to open program {program_name}: {str(e)}")
        messagebox.showerror("Error", f"Failed to open program {program_name}")

# Function to check for updates by comparing the build version with GitHub releases
def check_for_update():
    try:
        response = requests.get('https://api.github.com/repos/devinalonzo/myprogram/releases/latest')
        latest_version = response.json()['tag_name']
        
        current_version = read_version()
        logging.info(f"Current version: {current_version}, Latest version: {latest_version}")
        
        if current_version < latest_version:
            # Update available
            messagebox.showinfo("Update Available", f"New version {latest_version} available!")
            download_and_update(latest_version)
        else:
            # No update necessary
            messagebox.showinfo("Up to Date", f"You have the latest version: {current_version}")
            logging.info("No update necessary")
    except Exception as e:
        logging.error(f"Failed to check for updates: {str(e)}")
        messagebox.showerror("Update Error", "Failed to check for updates.")

# Function to download and update the program
def download_and_update(latest_version):
    try:
        update_url = f'https://github.com/devinalonzo/myprogram/releases/download/{latest_version}/DevinsProgram_{latest_version}.exe'
        update_path = os.path.join(STATIC_FOLDER, f'DevinsProgram_{latest_version}.exe')
        
        response = requests.get(update_url)
        with open(update_path, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded update: {update_path}")
        
        # Run the new version after download
        subprocess.Popen([update_path])
        sys.exit(0)
    except Exception as e:
        logging.error(f"Failed to download update: {str(e)}")
        messagebox.showerror("Update Error", "Failed to download the update.")

# Function to read the current version from version.txt
def read_version():
    try:
        with open(os.path.join(STATIC_FOLDER, "version.txt"), 'r') as f:
            version = f.read().strip()
            return version
    except Exception as e:
        logging.error(f"Failed to read version: {str(e)}")
        return "BETA"

# GUI to show the available programs
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")
    
    # Set window size to 1200x600
    window_width = 1200
    window_height = 600
    root.geometry(f"{window_width}x{window_height}")
    
    # Set the window icon using the .png file
    try:
        icon_image = ImageTk.PhotoImage(file=ICON_PATH)
        root.iconphoto(True, icon_image)
    except Exception as e:
        logging.error(f"Failed to load icon: {str(e)}")

    # Load and set background image
    try:
        background_image = Image.open(BACKGROUND_PATH)
        background_image = background_image.resize((window_width, window_height), Image.LANCZOS)
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(root, image=background_photo)
        background_label.place(relwidth=1, relheight=1)
    except Exception as e:
        logging.error(f"Failed to load background: {str(e)}")

    # Button styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")

    # Load available programs from C:\DevinsFolder
    program_names = []
    if os.path.exists(STATIC_FOLDER):
        program_names = [f for f in os.listdir(STATIC_FOLDER) if f.endswith('.exe')]

    # Divide programs by type (prefix-based)
    pump_programs = [p for p in program_names if p.startswith('1-')]
    crind_programs = [p for p in program_names if p.startswith('2-')]
    veeder_root_programs = [p for p in program_names if p.startswith('3-')]
    passport_programs = [p for p in program_names if p.startswith('4-')]
    help_resources = [p for p in program_names if p.startswith('5-')]

    # Set positions for the program buttons
    columns = [
        ("Pump", pump_programs, 60, 140),
        ("CRIND", crind_programs, 380, 140),
        ("Veeder-Root", veeder_root_programs, 700, 140),
        ("Passport", passport_programs, 1020, 140)
    ]

    # Create and place buttons for programs
    for column_name, column_programs, column_x, column_y in columns:
        column_label = tk.Label(root, text=column_name, bg=button_bg, fg=button_fg, font=button_font)
        column_label.place(x=column_x, y=column_y - 40)
        
        for idx, program in enumerate(column_programs):
            display_name = program[2:-4]  # Remove prefix and extension
            button = tk.Button(root, text=display_name, bg=button_bg, fg=button_fg, font=button_font,
                               command=lambda p=program: open_program(p))
            button.place(x=column_x, y=column_y + (60 * idx))

    # Add Help/Resources buttons
    help_label = tk.Label(root, text="Help/Resources", bg=button_bg, fg=button_fg, font=button_font)
    help_label.place(x=60, y=400)
    
    for idx, help_program in enumerate(help_resources):
        display_name = help_program[2:-4]  # Remove prefix and extension
        button = tk.Button(root, text=display_name, bg=button_bg, fg=button_fg, font=button_font,
                           command=lambda p=help_program: open_program(p))
        button.place(x=60 + (idx % 3) * 320, y=400 + (60 * (idx // 3)))

    # Add AnyDesk and Update buttons
    anydesk_button = tk.Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font, command=open_anydesk)
    anydesk_button.place(x=1000, y=460)

    update_button = tk.Button(root, text="Check for Update", bg=button_bg, fg=button_fg, font=button_font,
                              command=check_for_update)
    update_button.place(x=1120, y=460)

    # Display the current version
    version_label = tk.Label(root, text=f"Version: {read_version()}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(x=1120, y=520)

    root.mainloop()

# Function to open AnyDesk
def open_anydesk():
    anydesk_path = os.path.join(STATIC_FOLDER, "AnyDesk.exe")
    if os.path.exists(anydesk_path):
        subprocess.Popen([anydesk_path])
    else:
        logging.info("AnyDesk not found, downloading...")
        # Download AnyDesk if not present
        url = 'https://download.anydesk.com/AnyDesk.exe'
        anydesk_dest = os.path.join(STATIC_FOLDER, 'AnyDesk.exe')
        response = requests.get(url)
        with open(anydesk_dest, 'wb') as f:
            f.write(response.content)
        subprocess.Popen([anydesk_dest])

if __name__ == "__main__":
    program_selection()
