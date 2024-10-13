import os
import sys
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox, Button, Frame
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

# Fetch the build version from the passed argument or default to BETA
CURRENT_VERSION = "BETA"
if hasattr(sys, '_MEIPASS'):
    try:
        with open(resource_path('version.txt'), 'r') as version_file:
            CURRENT_VERSION = version_file.read().strip()
    except Exception as e:
        print(f"Error loading version: {e}")
else:
    CURRENT_VERSION = "BETA"

# Check for updates and compare the version from GitHub repo with current version
def check_for_update():
    try:
        response = requests.get(GITHUB_RELEASES_URL)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            if latest_version > CURRENT_VERSION:  # Only update if the latest version is newer
                download_url = latest_release["assets"][0]["browser_download_url"]
                file_name = latest_release["assets"][0]["name"]
                if download_latest_exe(download_url, file_name):
                    messagebox.showinfo("Update Available", f"New version {latest_version} downloaded. Saved on your Desktop as {file_name}. Please restart the program.")
                else:
                    messagebox.showerror("Update Failed", "Failed to download the latest EXE.")
            else:
                messagebox.showinfo("No Update", f"You are already using the latest version ({CURRENT_VERSION}).")
        else:
            messagebox.showerror("Error", "Failed to check for updates.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check for updates: {e}")

# Download the latest EXE from GitHub and save it to the desktop
def download_latest_exe(download_url, file_name):
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            exe_path = os.path.join(os.path.expanduser('~'), 'Desktop', file_name)
            with open(exe_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading EXE: {e}")
    return False

# AnyDesk button behavior: Download if not found, otherwise open
def open_anydesk():
    if not os.path.exists(ANYDESK_PATH):
        response = requests.get(ANYDESK_DOWNLOAD_URL)
        if response.status_code == 200:
            with open(ANYDESK_PATH, 'wb') as f:
                f.write(response.content)
            messagebox.showinfo("AnyDesk", "AnyDesk downloaded and opened.")
        else:
            messagebox.showerror("Error", "Failed to download AnyDesk.")
    subprocess.Popen(ANYDESK_PATH, shell=True)

# Open a selected program from the EXE folder
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
    root.state('zoomed')  # Open maximized, but not full-screen
    root.resizable(False, False)  # Lock the window size

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

    # Set the screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Load and set background image (more efficient)
    background_image = Image.open(BACKGROUND_PATH).resize((screen_width, screen_height), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Button styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")

    # Header styling with red neon glow effect
    header_style = {"bg": "#2c3e50", "fg": "#ff3b3b", "font": ("Helvetica", 16, "bold")}

    # Create labels for the columns with header glow effect
    columns = [
        ("Pump", pump_programs, screen_width // 5 * 0),
        ("CRIND", crind_programs, screen_width // 5 * 1),
        ("Veeder-Root", veeder_root_programs, screen_width // 5 * 2),
        ("Passport", passport_programs, screen_width // 5 * 3)
    ]

    # Place programs into their respective columns and make buttons resizable
    for column_name, column_programs, column_x in columns:
        column_label = tk.Label(root, text=column_name, **header_style)
        column_label.place(x=column_x + 50, y=30)
        for idx, program_name in enumerate(column_programs[:8]):  # Limit each column to 8 programs
            program_display_name = os.path.splitext(program_name)[0][2:]  # Strip the first 2 characters (number-)
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=column_x + 50, y=80 + idx * 40, width=screen_width // 5 - 100)  # Adjust button width

    # Add Help/Resources section at the halfway point
    help_label = tk.Label(root, text="Help/Resources", **header_style)
    help_label.place(x=50, y=screen_height // 2)  # Halfway down the screen
    for idx, program_name in enumerate(help_resources):
        program_display_name = os.path.splitext(program_name)[0][2:]  # Strip the first 2 characters (5-)
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                        command=lambda name=program_name: open_program(name))
        button.place(x=50 + idx * 250, y=screen_height // 2 + 50, width=200)  # Adjust button width

    # Frame for AnyDesk and Update buttons side-by-side, moved higher
    button_frame = Frame(root, bg="#2c3e50")
    button_frame.place(x=screen_width - 500, y=screen_height - 200)  # Moved higher up

    # Add AnyDesk and Update buttons with extra padding
    anydesk_button = Button(button_frame, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font,
                            command=open_anydesk)
    anydesk_button.pack(side=tk.LEFT, padx=10, pady=10)

    update_button = Button(button_frame, text="Check for Update", bg=button_bg, fg=button_fg, font=button_font,
                           command=check_for_update)
    update_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Display version number in the bottom-right corner
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    root.mainloop()

# Run the program selection UI
if __name__ == "__main__":
    program_selection()
