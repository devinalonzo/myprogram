import os
import subprocess
import webbrowser
import ctypes
import shutil

# Define the paths
exe_path = os.path.join(os.path.expanduser('~'), 'Gilbarco', 'M7MaintenanceTool', 'M7MaintenanceTool-1.4.6.jar')
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/FlexPayIV/FlexPayIVMaintenanceTool/M7MaintenanceTool-1.4.6-r38108-install.exe"
bat_path = os.path.join(os.path.expanduser('~'), 'Gilbarco', 'M7MaintenanceTool', 'M7_MaintenanceRun.bat')
shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Flex 4 M7Tool.lnk")

# Function to show a message box
def show_message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# Function to create the batch file
def create_bat_file(path):
    bat_content = """@echo on

@setlocal enableextensions
@cd /d "%~dp0"
echo %cd%
Set RUN_JVM_ARGS=XX:+UseConcMarkSweepGC
start javaw -jar %~dp0M7MaintenanceTool-1.4.5.jar
"""
    with open(path, 'w') as bat_file:
        bat_file.write(bat_content)

# Function to create a shortcut
def create_shortcut(target, shortcut_path):
    import pythoncom
    from win32com.shell import shell
    
    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    shell_link.SetPath(target)
    shell_link.SetDescription("Shortcut to Flex 4 M7Tool")
    shell_link.SetWorkingDirectory(os.path.dirname(target))

    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)

# Check if the executable exists
if os.path.exists(exe_path):
    # If the executable is found, check for the batch file
    if not os.path.exists(bat_path):
        print("Batch file not found. Creating batch file...")
        create_bat_file(bat_path)
    else:
        print("Batch file already exists.")

    # Create a shortcut to the batch file on the desktop
    print("Creating shortcut to batch file on the desktop...")
    create_shortcut(bat_path, shortcut_path)

    # Launch the application
    print("Launching M7MaintenanceTool...")
    subprocess.Popen(["javaw", "-jar", exe_path], shell=True)
else:
    # If not found, open the installer link in the default web browser
    print("M7MaintenanceTool not found. Opening installer link in web browser...")
    webbrowser.open(installer_url)
    show_message_box("Installer Needed", "The installer will be downloaded. Please follow the instructions to install M7 Maintenance Tool. After installation, please click 'Flex 4' again to launch the application.")
