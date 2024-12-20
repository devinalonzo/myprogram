import os
import subprocess
import webbrowser
import ctypes
from tkinter import simpledialog, Tk

# Define the paths
exe_path = os.path.join(os.path.expanduser('~'), 'Gilbarco', 'M7MaintenanceTool', 'M7MaintenanceTool-1.4.6.jar')
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/FlexPayIV/FlexPayIVMaintenanceTool/M7MaintenanceTool-1.4.6-r38108-install.exe"
temp_dir = r"C:\M7TempFiles"

# Function to show a message box
def show_message_box(title, text):
    return ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# Function to run a command with admin rights
def run_as_admin(command, cwd=None):
    params = ["powershell", "-Command", f"Start-Process -FilePath '{command[0]}' -ArgumentList '{' '.join(command[1:])}' -Verb RunAs"]
    subprocess.run(params, shell=True, cwd=cwd)

# Function to get the number of instances to run
def get_instance_count():
    root = Tk()
    root.withdraw()  # Hide the root window
    user_input = simpledialog.askinteger("Number of Instances", "Enter the number of instances you want to open (1-10):")
    if user_input is None or not (1 <= user_input <= 10):
        return 1
    return user_input

# Create the temporary directory if it doesn't exist
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Check if the executable exists
if os.path.exists(exe_path):
    # Get the number of instances to open
    instance_count = get_instance_count()

    # Launch the application with admin rights from the temp directory
    for _ in range(instance_count):
        print(f"Launching M7MaintenanceTool instance {_ + 1} with admin rights from {temp_dir}...")
        run_as_admin(["javaw", "-jar", exe_path], cwd=temp_dir)
else:
    # If not found, open the installer link in the default web browser
    print("M7MaintenanceTool not found. Opening installer link in web browser...")
    webbrowser.open(installer_url)
    show_message_box("Installer Needed", "The installer will be downloaded. Please follow the instructions to install M7 Maintenance Tool. After installation, please click 'Flex 4' again to launch the application.")
