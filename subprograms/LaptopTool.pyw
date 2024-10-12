import os
import webbrowser
import ctypes

# Define the path to the executable
exe_path = r"C:\gilbarco\NGD\bin\LaptopTool.exe"
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/files/dialog_singleclick_v20_0_20.exe"

# Function to show a message box
def show_message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# Check if the executable exists
if os.path.exists(exe_path):
    # If the executable is found, launch it
    print("LaptopTool.exe found. Launching application...")
    os.startfile(exe_path)
else:
    # If not found, open the installer link in the default web browser
    print("LaptopTool.exe not found. Opening installer link in web browser...")
    webbrowser.open(installer_url)
    show_message_box("Installer Needed", "When the download is complete, please open it and enter your credentials for signing into GOLD Docs. (It usually works for me if I type random user and password but you do you). For the modifier enter 'blink' - without \" \". Then click 'UPDATE FILES'. This will install the NGD Laptop tool for you that will allow you to pull pump (PCN) logs, update door nodes, etc. After the installation is completed, click the LaptopTool button again to run.")
