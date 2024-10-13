import os
import sys
import requests
import subprocess
import shutil
import time

# GitHub URLs
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
SUBPROGRAMS_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/subprograms/"
UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"
GITHUB_SUBPROGRAMS_API = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"

# Paths
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')  # Save EXE to the desktop
WORKING_DIR = os.path.join(os.getcwd(), 'dist')  # Temporary working directory
MAIN_PROGRAM_PATH = os.path.join(WORKING_DIR, 'mainprogram.pyw')
UPDATER_PATH = os.path.join(WORKING_DIR, 'updater.pyw')
SUBPROGRAMS_PATH = os.path.join(WORKING_DIR, 'subprograms')

# Create necessary directories
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)
if not os.path.exists(SUBPROGRAMS_PATH):
    os.makedirs(SUBPROGRAMS_PATH)

def log_message(message):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def download_file(url, dest_path):
    """Download a file from a URL."""
    log_message(f"Downloading {url}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        log_message(f"Downloaded {dest_path}")
    else:
        log_message(f"Failed to download {url}, status code: {response.status_code}")

def get_subprogram_files():
    """Fetch the list of files in the GitHub subprograms folder."""
    log_message("Fetching subprogram list from GitHub...")
    response = requests.get(GITHUB_SUBPROGRAMS_API)
    if response.status_code == 200:
        files = response.json()
        return [file['name'] for file in files if file['type'] == 'file']
    else:
        log_message(f"Failed to fetch subprogram list from GitHub, status code: {response.status_code}")
        return []

def download_all_files():
    """Download the main program, updater, and subprograms."""
    download_file(MAIN_PROGRAM_URL, MAIN_PROGRAM_PATH)
    download_file(UPDATER_URL, UPDATER_PATH)
    
    subprogram_files = get_subprogram_files()
    if not subprogram_files:
        log_message("No subprograms to download.")
    for subprogram in subprogram_files:
        download_file(f"{SUBPROGRAMS_URL}{subprogram}", os.path.join(SUBPROGRAMS_PATH, subprogram))

def generate_spec_file():
    """Generate the PyInstaller spec file dynamically."""
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    [r'{MAIN_PROGRAM_PATH}', r'{UPDATER_PATH}'],  # Use raw strings here to avoid Unicode escape issues
    pathex=[r'{WORKING_DIR}'],  # Use raw strings here as well
    binaries=[],
    datas=[(r'{SUBPROGRAMS_PATH}', 'subprograms')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyProgram',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyProgram'
)
"""
    with open(os.path.join(WORKING_DIR, "myprogram.spec"), 'w') as spec_file:
        spec_file.write(spec_content)
    log_message("Spec file generated.")

def create_exe():
    """Run PyInstaller to create the EXE."""
    log_message("Running PyInstaller to create the EXE...")
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--distpath", DESKTOP_PATH,  # Save the EXE to the desktop
        os.path.join(WORKING_DIR, "myprogram.spec")
    ])
    log_message("EXE created successfully on the desktop.")

def clean_up():
    """Remove temporary build files."""
    log_message("Cleaning up temporary build files...")
    shutil.rmtree(os.path.join(WORKING_DIR, 'build'), ignore_errors=True)
    shutil.rmtree(os.path.join(WORKING_DIR, '__pycache__'), ignore_errors=True)
    os.remove(os.path.join(WORKING_DIR, "myprogram.spec"))
    log_message("Clean up complete.")

if __name__ == "__main__":
    log_message("Starting EXE packaging process.")
    download_all_files()
    generate_spec_file()
    create_exe()
    clean_up()
    log_message("Packaging process complete.")
