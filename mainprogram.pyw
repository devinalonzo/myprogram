import os
import sys
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox, Button
from PIL import Image, ImageTk

# GitHub API URL for releases
GITHUB_RELEASES_URL = "https://api.github.com/repos/devinalonzo/myprogram/releases/latest"
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")

# Helper function to resolve paths whether running from script or EXE
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller bundled files """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Set the correct paths for programs and resources
PROGRAMS_PATH = resource_path('subprograms')
BACKGROUND_PATH = resource_path('bkgd.png')
ICON_PATH = resource_path('ico.png')  # Use the .png icon

# Function to get the latest release version from GitHub
def fetch_latest_version():
    try:
        response = requests.get(GITHUB_RELEASES_URL)
        if response.status_code == 200:
            latest_release = response.json()
            return latest_release["tag_name"], latest_release["html_url"]
        else:
            return "BETA", None
    except Exception as e:
        print(f"Error fetching latest version: {e}")
        return "BETA", None

# Load the version dynamically during runtime
CURRENT_VERSION, release_url = fetch_latest_version()

# Check for updates and download latest EXE from GitHub if available
def check_for_update():
    latest_version, _ = fetch_latest_version()
    if latest_version != CURRENT_VERSION:
        if download_latest_exe():
            messagebox.showinfo("Update Available", f"New version {latest_version} downloaded. Please restart the program.")
        else:
            messagebox.showerror("Update Failed", "Failed to download the latest EXE.")
    else:
        messagebox.showinfo("No Update", f"You are already using the latest version ({CURRENT_VERSION}).")

# Download the latest EXE from GitHub and replace the current one
def download_latest_exe():
    if release_url:
        response = requests.get(f"{release_url}/download/mainprogram.exe")
        if response.status_code == 200:
            exe_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'mainprogram.exe')
            with open(exe_path, 'wb') as f:
                f.write(response.content)
            return True
    return False

# Open a selected program from the EXE folder instead of .pyw files
def open_program(program_name):
    exe_name = os.path.splitext(program_name)[0] + ".exe"
    program_path = resource_path(os.path.join('subprograms', exe_name))
    
    if os.path.exists(program_path):
        subprocess.Popen([program_path], shell=True)
    else:
        messagebox.showinfo("Error", f"EXE not found:\n{program_path}")

# Program selection UI
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")

    # Set the window icon using the .png file
    icon_image = ImageTk.PhotoImage(file=ICON_PATH)
    root.iconphoto(True, icon_image)

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
            if program_name.startswith('pu-'):
                pump_programs.append(program_name)
            elif program_name.startswith('c-'):
                crind_programs.append(program_name)
            elif program_name.startswith('v-'):
                veeder_root_programs.append(program_name)
            elif program_name.startswith('pa-'):
                passport_programs.append(program_name)
            elif program_name.startswith('h-'):
                help_resources.append(program_name)

    # Calculate necessary window size based on the number of programs
    max_rows = max(len(pump_programs), len(crind_programs), len(veeder_root_programs), len(passport_programs), 8)
    window_height = 100 + (max_rows * 40)
    window_width = 900
    root.geometry(f"{window_width}x{window_height}")
    root.minsize(window_width, window_height)  # Set a minimum size for the window

    # Load and set background image
    background_image = Image.open(BACKGROUND_PATH)
    background_image = background_image.resize((window_width, window_height), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

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
            program_display_name = os.path.splitext(program_name)[0][3:]  # Remove prefix
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=column_x, y=60 + idx * 40)

    # Add Help/Resources section at the bottom
    help_label = tk.Label(root, text="Help/Resources", bg=button_bg, fg=button_fg, font=button_font)
    help_label.place(x=50, y=window_height - 100)
    for idx, program_name in enumerate(help_resources):
        program_display_name = os.path.splitext(program_name)[0][2:]  # Remove 'h-' prefix
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                        command=lambda name=program_name: open_program(name))
        button.place(x=50 + idx * 150, y=window_height - 60)

    # Display version number in the bottom-right corner
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    root.mainloop()

# Run the program selection UI
if __name__ == "__main__":
    program_selection()
