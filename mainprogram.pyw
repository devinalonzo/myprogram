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
UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"
UPDATER_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "updater.pyw")  # Corrected missing parenthesis

# Helper function to resolve paths whether running from script or EXE
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller bundled files """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Set the correct paths for programs and resources
PROGRAMS_PATH = resource_path('subprograms')
BACKGROUND_PATH = resource_path('bkgd.png')

# Function to get the latest release version from GitHub
def fetch_latest_version():
    try:
        response = requests.get(GITHUB_RELEASES_URL)
        if response.status_code == 200:
            latest_release = response.json()
            return latest_release["tag_name"], latest_release["html_url"]  # Return version and release URL
        else:
            return "BETA", None  # If no releases found, return BETA
    except Exception as e:
        print(f"Error fetching latest version: {e}")
        return "BETA", None

# Load the version dynamically during runtime
CURRENT_VERSION, release_url = fetch_latest_version()

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

# Check if there's a newer version of the EXE available on GitHub
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
    if release_url:  # Use the release URL from the GitHub API
        response = requests.get(f"{release_url}/download/mainprogram.exe")
        if response.status_code == 200:
            exe_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'mainprogram.exe')
            with open(exe_path, 'wb') as f:
                f.write(response.content)
            return True  # Return success
    return False  # Return failure if download fails

# Open a selected program from the EXE folder instead of .pyw files
def open_program(program_name):
    exe_name = os.path.splitext(program_name)[0] + ".exe"  # Look for the EXE version
    program_path = resource_path(os.path.join('subprograms', exe_name))  # Ensure EXE path
    
    if os.path.exists(program_path):
        subprocess.Popen([program_path], shell=True)
    else:
        messagebox.showinfo("Open Program", f"'{exe_name}' not found.")

# Program selection UI
def program_selection():
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

    # List programs from the local directory or EXE-bundled folder
    if os.path.exists(PROGRAMS_PATH):
        programs = os.listdir(PROGRAMS_PATH)
        if programs:
            for idx, program_name in enumerate(programs):
                program_display_name = os.path.splitext(program_name)[0]
                button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                                command=lambda name=program_name: open_program(name))
                button.place(x=350, y=150 + idx * 50)
        else:
            messagebox.showinfo("No Programs Found", "No subprograms are available in the subprograms folder.")
    else:
        messagebox.showinfo("No Programs Found", "Subprograms folder not found!")

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

# Open AnyDesk if installed, otherwise download it
def open_anydesk():
    if not os.path.exists(ANYDESK_PATH):
        response = requests.get(ANYDESK_DOWNLOAD_URL)
        with open(ANYDESK_PATH, 'wb') as f:
            f.write(response.content)
    os.startfile(ANYDESK_PATH)

# Run the program selection UI
if __name__ == "__main__":
    program_selection()
