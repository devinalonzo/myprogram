import os
import subprocess
import urllib.request
import shutil

# Define the path to the executable
exe_path = r"C:\Program Files (x86)\Gilbarco\FlexPayMaintenance\FlexpayMaintenance.exe"
installer_url = "https://interactive.gilbarco.com/apps/tech_resource/laptop/SPOTUpdate/FlexPayMaintenance_setup_3_0_1_8.exe"
temp_installer_path = os.path.join(os.getenv('TEMP'), "FlexPayMaintenance_setup.exe")

# Check if the executable exists
if os.path.exists(exe_path):
    # If the executable is found, open it
    print("FlexPayMaintenance.exe found. Launching application...")
    subprocess.Popen([exe_path], shell=True)
else:
    # If not found, download the installer
    print("FlexPayMaintenance.exe not found. Downloading installer...")
    try:
        with urllib.request.urlopen(installer_url) as response, open(temp_installer_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Installer downloaded successfully.")

        # Run the installer
        print("Running the installer...")
        subprocess.Popen([temp_installer_path], shell=True)
    except Exception as e:
        print(f"Failed to download or run the installer: {e}")
