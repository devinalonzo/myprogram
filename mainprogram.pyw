import os
import requests
import tkinter as tk
from tkinter import messagebox, Button
import subprocess
import sys
from PIL import Image, ImageTk

# Constants for GitHub URLs
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/version.txt"
BACKGROUND_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/bkgd.png"
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"
UPDATER_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "updater.pyw")

# Helper function to resolve paths whether running from script or EXE
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller bundled files """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Set the correct paths for programs and resources
PROGRAMS_PATH = resource_path('subprograms')
BACKGROUND_PATH = resource_path('bkgd.png')

# Function to get the version number from GitHub
def fetch_version():
    try:
        response = requests.get(GITHUB_VERSION_URL)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "1.0.0"  # Default version if there's an issue
    except Exception as e:
        print(f"Error fetching version: {e}")
        return "1.0.0"

# Load the version dynamically during build
CURRENT_VERSION = fetch_version()

# Ensure directories exist
def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)

# Download the background image from GitHub
def download_background():
    response = requests.get(BACKGROUND_URL)
    if response.status_code == 200:
        with open(BACKGROUND_PATH, 'wb') as f:
            f.write(response.content)
    else:
        messagebox.showerror("Error", "Failed to download background image. Check your internet connection.")
        return False
    return True

# Download the updater script from GitHub
def download_updater():
    response = requests.get(UPDATER_URL)
    if response.status_code == 200:
        with open(UPDATER_PATH, 'wb') as f:
            f.write(response.content)
    else:
        messagebox.showerror("Error", "Failed to download updater program.")
        return False
    return True

# Update the main program by running the updater script
def update_main_program():
    if not os.path.exists(UPDATER_PATH):
        if not download_updater():
            return
    subprocess.Popen([sys.executable, UPDATER_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Check if there's a newer version of the EXE available
def check_for_update():
    response = requests.get(GITHUB_VERSION_URL)
    if response.status_code == 200:
        latest_version = response.text.strip()
        if latest_version != CURRENT_VERSION:
            download_latest_exe()  # Implement this function to download EXE
            messagebox.showinfo("Update Available", "New version downloaded. Please restart the program.")
        else:
            messagebox.showinfo("No Update", "You already have the latest version.")
    else:
        messagebox.showerror("Error", "Could not check for updates.")

# Download the latest EXE from GitHub and replace the current one
def download_latest_exe():
    url = "https://github.com/devinalonzo/myprogram/releases/latest/download/mainprogram.exe"
    response = requests.get(url)
    if response.status_code == 200:
        exe_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'mainprogram.exe')
        with open(exe_path, 'wb') as f:
            f.write(response.content)
        messagebox.showinfo("Success", "Updated to the latest version.")
    else:
        messagebox.showerror("Error", "Failed to download the latest EXE.")

# Program selection UI
def program_selection():
    ensure_directories()
    if not os.path.exists(BACKGROUND_PATH):
        download_background()

    root = tk.Tk()
    root.title("Devin's Program")
    root.geometry("800x600")

    # Load and set background image
    background_image = Image.open(BACKGROUND_PATH)
    background_image = background_image.resize((800, 600), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Button styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")

    # List programs from the local directory
    programs = os.listdir(PROGRAMS_PATH)
    if programs:
        for idx, program_name in enumerate(programs):
            program_display_name = os.path.splitext(program_name)[0]
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=350, y=150 + idx * 50)
    else:
        messagebox.showinfo("No Programs Found", "No subprograms are available in the subprograms folder.")

    # AnyDesk button
    anydesk_button = Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font, command=open_anydesk)
    anydesk_button.place(x=650, y=20)

    # Update button
    update_button = Button(root, text="Update", bg=button_bg, fg=button_fg, font=button_font, command=check_for_update)
    update_button.place(x=550, y=20)

    # Version Label at bottom right
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # Positioned bottom-right with padding

    root.mainloop()

# Open a selected program from the local folder
def open_program(program_name):
    program_path = os.path.join(PROGRAMS_PATH, program_name)
    if os.path.exists(program_path):
        os.startfile(program_path)
    else:
        messagebox.showinfo("Open Program", f"'{program_name}' not found. Please sync again.")

# Open AnyDesk if installed, otherwise download it
def open_anydesk():
    if not os.path.exists(ANYDESK_PATH):
        response = requests.get(ANYDESK_DOWNLOAD_URL)
        with open(ANYDESK_PATH, 'wb') as f:
            f.write(response.content)
    os.startfile(ANYDESK_PATH)

if __name__ == "__main__":
    program_selection()
