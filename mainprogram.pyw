import os
import sys
import tkinter as tk
from tkinter import messagebox, Button, Label
from PIL import Image, ImageTk
import subprocess

# Define relative paths
ICON_PATH = "ico.png"  # Replace with correct icon path
BACKGROUND_PATH = "bkgd.png"
PROGRAMS_PATH = "subprograms"
CURRENT_VERSION = "1.0.0"  # This should be dynamically set during the build process

# Helper function to resolve file paths when bundled with PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller uses this temp folder for packaged files
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Function to open a subprogram (EXE file)
def open_program(full_filename):
    subprograms_dir = resource_path(PROGRAMS_PATH)
    full_prog_path = os.path.join(subprograms_dir, full_filename)
    
    if os.path.exists(full_prog_path):
        subprocess.Popen([full_prog_path], shell=True)
    else:
        messagebox.showerror("EXE not found", f"{full_prog_path} not found.")

# Function to open AnyDesk
def open_anydesk():
    anydesk_path = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
    if os.path.exists(anydesk_path):
        subprocess.Popen([anydesk_path], shell=True)
    else:
        # Download and save it to the desktop if not found
        anydesk_url = "https://download.anydesk.com/AnyDesk.exe"
        subprocess.run(["powershell", "-command", f"Invoke-WebRequest -Uri {anydesk_url} -OutFile {anydesk_path}"])
        subprocess.Popen([anydesk_path], shell=True)

# Function to check for updates
def check_for_update():
    # Placeholder: Logic to compare the current version with the latest on GitHub
    pass

# Main program selection UI
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")

    # Set the window icon using the .png file
    icon_path = resource_path(ICON_PATH)
    if os.path.exists(icon_path):
        icon_image = ImageTk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon_image)
    else:
        messagebox.showerror("Icon not found", f"Icon file '{ICON_PATH}' not found.")

    # Group programs by their category prefix
    pump_programs = []
    crind_programs = []
    veeder_root_programs = []
    passport_programs = []
    help_resources = []

    # Use the resource_path to find the subprograms path
    subprograms_path = resource_path(PROGRAMS_PATH)
    
    # List programs from the local directory or EXE-bundled folder
    if os.path.exists(subprograms_path):
        programs = os.listdir(subprograms_path)
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
    window_height = 100 + (max_rows * 40)
    window_width = 900
    root.geometry(f"{window_width}x{window_height}")
    root.minsize(window_width, window_height)  # Set a minimum size for the window

    # Load and set background image
    background_path = resource_path(BACKGROUND_PATH)
    if os.path.exists(background_path):
        background_image = Image.open(background_path)
        background_image = background_image.resize((window_width, window_height), Image.LANCZOS)
        background_photo = ImageTk.PhotoImage(background_image)
        background_label = tk.Label(root, image=background_photo)
        background_label.place(relwidth=1, relheight=1)
    else:
        messagebox.showerror("Background not found", f"Background file '{BACKGROUND_PATH}' not found.")

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
            program_display_name = os.path.splitext(program_name)[0][2:]  # Remove number prefix for display
            button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                            command=lambda name=program_name: open_program(name))
            button.place(x=column_x, y=60 + idx * 40)

    # Add Help/Resources section at the bottom
    help_label = tk.Label(root, text="Help/Resources", bg=button_bg, fg=button_fg, font=button_font)
    help_label.place(x=50, y=window_height - 100)
    for idx, program_name in enumerate(help_resources):
        program_display_name = os.path.splitext(program_name)[0][2:]  # Remove '5-' prefix
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                        command=lambda name=program_name: open_program(name))
        button.place(x=50 + idx * 150, y=window_height - 60)

    # Add AnyDesk and Update buttons
    anydesk_button = Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font,
                            command=open_anydesk)
    anydesk_button.place(x=650, y=window_height - 100)

    update_button = Button(root, text="Check for Update", bg=button_bg, fg=button_fg, font=button_font,
                           command=check_for_update)
    update_button.place(x=650, y=window_height - 60)

    # Display version number in the bottom-right corner
    version_label = tk.Label(root, text=f"Version: {CURRENT_VERSION}", bg=button_bg, fg=button_fg, font=("Helvetica", 10))
    version_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    root.mainloop()

if __name__ == "__main__":
    program_selection()
