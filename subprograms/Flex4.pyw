import os
import subprocess
import webbrowser
import ctypes
import sys

# Define the paths
exe_path = os.path.join(os.path.expanduser('~'), 'Gilbarco', 'M7MaintenanceTool', 'M7MaintenanceTool-1.4.6.jar')
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/FlexPayIV/FlexPayIVMaintenanceTool/M7MaintenanceTool-1.4.6-r38108-install.exe"

# Function to show a message box
def show_message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# Function to run a command with admin rights
def run_as_admin(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

# Get user input for number of instances to run
try:
    num_instances = int(input("How many instances of the program would you like to open? "))
    if num_instances < 1:
        raise ValueError("The number of instances must be at least 1.")
except ValueError as e:
    print(f"Invalid input: {e}")
    sys.exit(1)

# Check if the executable exists
if os.path.exists(exe_path):
    # Launch the specified number of instances with admin rights
    print("Launching M7MaintenanceTool with admin rights...")
    for _ in range(num_instances):
        run_as_admin(["javaw", "-jar", exe_path])
else:
    # If not found, open the installer link in the default web browser
    print("M7MaintenanceTool not found. Opening installer link in web browser...")
    webbrowser.open(installer_url)
    show_message_box("Installer Needed", "The installer will be downloaded. Please follow the instructions to install M7 Maintenance Tool. After installation, please click 'Flex 4' again to launch the application.")
