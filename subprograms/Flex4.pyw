import os
import subprocess
import webbrowser
import ctypes

# Define the paths
exe_path = os.path.join(os.path.expanduser('~'), 'Gilbarco', 'M7MaintenanceTool', 'M7MaintenanceTool-1.4.6.jar')
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/FlexPayIV/FlexPayIVMaintenanceTool/M7MaintenanceTool-1.4.6-r38108-install.exe"

# Function to show a message box
def show_message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# Function to run a command with admin rights
def run_as_admin(command):
    params = " ".join(command)
    subprocess.run(["powershell", "-Command", f"Start-Process cmd -ArgumentList '/c {params}' -Verb RunAs"], shell=True)

# Check if the executable exists
if os.path.exists(exe_path):
    # Launch the application with admin rights
    print("Launching M7MaintenanceTool with admin rights...")
    run_as_admin(["javaw", "-jar", exe_path])
else:
    # If not found, open the installer link in the default web browser
    print("M7MaintenanceTool not found. Opening installer link in web browser...")
    webbrowser.open(installer_url)
    show_message_box("Installer Needed", "The installer will be downloaded. Please follow the instructions to install M7 Maintenance Tool. After installation, please click 'Flex 4' again to launch the application.")
