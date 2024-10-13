import os
import sys
import requests
import ctypes
import psutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# GitHub API URL for fetching subprograms
GITHUB_API_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/"
SUBPROGRAMS_PATH = "subprograms"
UPDATER_SCRIPT = "updater.pyw"
MAIN_PROGRAM_SCRIPT = "mainprogram.pyw"

# File paths for the EXE and data
UPDATER_FILE_PATH = "C:\\DevinsProgram\\updater.pyw"
MAIN_PROGRAM_DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', MAIN_PROGRAM_SCRIPT)
SUBPROGRAMS_DIR = "C:\\DevinsProgram\\subprograms"

# Ensure the DevinsProgram directory exists
if not os.path.exists(r"C:\DevinsProgram"):
    os.makedirs(r"C:\DevinsProgram")

# PyInstaller spec template with escaped curly braces and corrected file paths and argument ordering
spec_template = """
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['updater.pyw'],
    pathex=['.'],
    binaries=[],
    datas={datas},
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
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
    name='updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='updater'
)
"""

def log_message(message):
    print(message)

def fetch_github_files(api_url, path):
    """Fetch the list of files from a GitHub repository path."""
    response = requests.get(api_url + path)
    if response.status_code == 200:
        return response.json()
    else:
        log_message(f"Error fetching files from GitHub: {response.status_code}")
        return []

def create_spec_file(file_list):
    """Create a spec file based on the fetched GitHub files."""
    datas_entries = []

    # Add the main program and updater with escaped backslashes
    datas_entries.append(f"('{UPDATER_FILE_PATH.replace('\\', '\\\\')}', 'updater.pyw')")
    datas_entries.append(f"('{MAIN_PROGRAM_DESKTOP_PATH.replace('\\', '\\\\')}', 'Desktop/{MAIN_PROGRAM_SCRIPT}')")

    # Add the subprograms with escaped backslashes
    for file in file_list:
        file_name = file['name']
        file_entry = f"('{SUBPROGRAMS_DIR.replace('\\', '\\\\')}\\\\{file_name}', 'subprograms/{file_name}')"
        datas_entries.append(file_entry)

    # Format datas for the spec file
    datas_str = ", ".join(datas_entries)

    # Create the spec content by formatting the template
    spec_content = spec_template.format(datas=datas_str)

    # Save the spec file
    with open("updater.spec", "w") as spec_file:
        spec_file.write(spec_content)
    log_message("Spec file created successfully.")

def package_exe():
    """Run PyInstaller to package everything into an EXE."""
    log_message("Packaging the EXE using PyInstaller...")
    os.system("pyinstaller --noconfirm updater.spec")

def update_updater():
    """Download and replace the updater."""
    UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"
    log_message(f"Downloading the latest updater from {UPDATER_URL}")
    response = requests.get(UPDATER_URL, stream=True)
    if response.status_code == 200:
        with open(UPDATER_FILE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        log_message(f"Updater successfully updated.")
    else:
        log_message(f"Failed to download the updater, status code: {response.status_code}")

def main():
    # Ensure directories exist
    if not os.path.exists(SUBPROGRAMS_DIR):
        os.makedirs(SUBPROGRAMS_DIR)

    # Fetch the latest subprograms from GitHub
    log_message("Fetching the subprograms from GitHub...")
    subprogram_files = fetch_github_files(GITHUB_API_URL, SUBPROGRAMS_PATH)

    # Create the PyInstaller spec file
    log_message("Creating the PyInstaller spec file...")
    create_spec_file(subprogram_files)

    # Update the updater script itself
    log_message("Updating the updater script...")
    update_updater()

    # Run PyInstaller to package the EXE
    log_message("Running PyInstaller to build the EXE...")
    package_exe()

if __name__ == "__main__":
    main()
