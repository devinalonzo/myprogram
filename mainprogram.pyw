import os
import sys
import subprocess
from tkinter import Tk, Button, Label, messagebox
from PIL import Image, ImageTk

# Function to get the path for the resources in development and PyInstaller modes
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Function to open the subprogram
def open_program(program_name):
    exe_name = os.path.splitext(program_name)[0] + ".exe"
    program_path = resource_path(os.path.join('subprograms', exe_name))

    # Debugging: Show the path in a messagebox
    messagebox.showinfo("Debug Info", f"Attempting to open:\n{program_path}")

    if os.path.exists(program_path):
        subprocess.Popen([program_path], shell=True)
    else:
        messagebox.showinfo("Error", f"EXE not found:\n{program_path}")

# Function to get the version of the program
def get_build_version():
    return "1.0.2"  # Set the current version

# Main GUI
root = Tk()
root.title(f"Main Program - Version {get_build_version()}")
root.geometry("1200x700")  # Starting size, but will maximize

# Maximize the window but not full-screen mode (with taskbar)
root.state('zoomed')

# Load and display the background image
background_image_path = resource_path("bkgd.png")
bg_image = Image.open(background_image_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.ANTIALIAS)
bg_image_tk = ImageTk.PhotoImage(bg_image)

background_label = Label(root, image=bg_image_tk)
background_label.place(relwidth=1, relheight=1)

# Define columns and programs based on the naming convention
columns = {
    "Pump": [],
    "CRIND": [],
    "Veeder-Root": [],
    "Passport": [],
    "Help/Resources": []
}

# Scan the subprograms folder to populate the columns
subprograms_path = resource_path('subprograms')
for file_name in os.listdir(subprograms_path):
    if file_name.endswith('.exe'):
        column_index = file_name.split('-')[0]
        program_name = file_name[2:-4]  # Strip the first 2 characters and the .exe extension
        if column_index == "1":
            columns["Pump"].append(program_name)
        elif column_index == "2":
            columns["CRIND"].append(program_name)
        elif column_index == "3":
            columns["Veeder-Root"].append(program_name)
        elif column_index == "4":
            columns["Passport"].append(program_name)
        elif column_index == "5":
            columns["Help/Resources"].append(program_name)

# Function to create buttons for each program in the GUI
def create_program_buttons(column_name, programs, column_position):
    row_position = 1
    for program in programs:
        program_button = Button(root, text=program, command=lambda p=program: open_program(p))
        program_button.grid(row=row_position, column=column_position, padx=10, pady=10, sticky="ew")
        row_position += 1

# Add header labels and buttons for each column
column_names = ["Pump", "CRIND", "Veeder-Root", "Passport", "Help/Resources"]
for idx, column_name in enumerate(column_names):
    header = Label(root, text=column_name, font=("Helvetica", 14, "bold"), relief="solid", bg="black", fg="red")
    header.grid(row=0, column=idx, padx=5, pady=5, sticky="ew")
    create_program_buttons(column_name, columns[column_name], idx)

# Help/Resources section - move it slightly higher
help_resources_label = Label(root, text="Help/Resources", font=("Helvetica", 14, "bold"), relief="solid", bg="black", fg="red")
help_resources_label.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
create_program_buttons("Help/Resources", columns["Help/Resources"], 4)

# Button to check for updates
def check_for_update():
    current_version = get_build_version()
    # Compare with the latest release on GitHub
    latest_version = "1.0.2"  # Placeholder for actual GitHub release check logic
    if latest_version > current_version:
        update_path = os.path.join(os.path.expanduser("~/Desktop"), f"mainprogram_{latest_version}.exe")
        # Download logic to fetch the latest version EXE from GitHub
        messagebox.showinfo("Update", f"Downloaded latest version {latest_version} to {update_path}")
    else:
        messagebox.showinfo("Update", "You already have the latest version.")

update_button = Button(root, text="Update", command=check_for_update)
update_button.grid(row=10, column=3, padx=10, pady=10, sticky="e")

# AnyDesk button functionality
def open_anydesk():
    anydesk_path = os.path.join(os.path.expanduser("~/Desktop"), "AnyDesk.exe")
    if not os.path.exists(anydesk_path):
        # Download AnyDesk and save it to desktop if not found
        # Add download logic here
        messagebox.showinfo("Downloading", "Downloading AnyDesk to your desktop...")
    subprocess.Popen([anydesk_path], shell=True)

anydesk_button = Button(root, text="AnyDesk", command=open_anydesk)
anydesk_button.grid(row=10, column=4, padx=10, pady=10, sticky="w")

# Start the main loop
root.mainloop()
