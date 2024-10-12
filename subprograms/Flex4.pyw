import os
import subprocess
import webbrowser
import ctypes
import shutil

# Define the path to the executable and other files
exe_path = r"C:\Users\kubat_admin\Gilbarco\M7MaintenanceTool\M7MaintenanceTool-1.4.5.jar"
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/FlexPayIV/FlexPayIVMaintenanceTool/M7MaintenanceTool-1.4.6-r38108-install.exe"
batch_file_path = r"C:\Users\kubat_admin\Gilbarco\M7MaintenanceTool\M7_MaintenanceRun.bat"
shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Flex 4 M7Tool.lnk")

# Function to show a message box
def show_message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 1)

# Function to create the batch file
def create_batch_file():
    batch_content = """echo on

@setlocal enableextensions
@cd /d "%~dp0"
echo %cd%
Set RUN_JVM_ARGS=XX:+UseConcMarkSweepGC
start   javaw  -jar   %~dp0M7MaintenanceTool-1.4.5.jar
"""
    with open(batch_file_path, 'w') as batch_file:
        batch_file.write(batch_content)

# Function to create a shortcut to the batch file
def create_shortcut():
    import pythoncom
    from win32com.shell import shell, shellcon
    
    shell_link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    shell_link.SetPath(batch_file_path)
    shell_link.SetDescription("Shortcut to M7 Maintenance Tool")
    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(shortcut_path, 0)

# Check if the executable exists
if os.path.exists(exe_path):
    # If the executable is found, open it
    print("M7MaintenanceTool-1.4.5.jar found. Launching application...")
    subprocess.Popen(["javaw", "-jar", exe_path], shell=True)
    
    # Check if the batch file exists, if not create it
    if not os.path.exists(batch_file_path):
        print("Batch file not found. Creating batch file...")
        create_batch_file()
        print("Batch file created successfully.")
    
    # Create a shortcut to the batch file on the desktop
    if not os.path.exists(shortcut_path):
        print("Creating shortcut on desktop...")
        create_shortcut()
        print("Shortcut created successfully.")
else:
    # If not found, open the installer link in the default web browser
    print("M7MaintenanceTool-1.4.5.jar not found. Opening installer link in web browser...")
    webbrowser.open(installer_url)
    show_message_box("Installer Needed", "The installer will be downloaded. Please follow the instructions to install the M7 Maintenance Tool. After installation, please click 'Flex 4' again to launch the application.")
