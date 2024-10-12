import os
import subprocess
import webbrowser

# Define the path to the executable
exe_path = r"C:\Program Files (x86)\Gilbarco\FlexPayMaintenance\FlexpayMaintenance.exe"
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/SPOTUpdate/FlexPayMaintenance_setup_3_0_1_8.exe"

# Check if the executable exists
if os.path.exists(exe_path):
    # If the executable is found, open it
    print("FlexPayMaintenance.exe found. Launching application...")
    subprocess.Popen([exe_path], shell=True)
else:
    # If not found, open the installer link in the default web browser
    print("FlexPayMaintenance.exe not found. Opening installer link in web browser...")
    print("The installer will be downloaded. Please follow the instructions to install FlexPay Maintenance. After installation, please click 'Flex 2' again to launch the application.")
    webbrowser.open(installer_url)
