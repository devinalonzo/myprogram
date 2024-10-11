import os
import requests
import tkinter as tk
from tkinter import Label, messagebox
import time
import signal
import psutil
import sys

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
PROGRAMS_PATH = r"C:\DevinsProgram\Programs"
MAIN_PROGRAM_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "mainprogram.pyw")
LOG_FILE_PATH = os.path.join(r"C:\DevinsProgram", "logs.txt")


def log_message(message):
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"{message}\n")
    print(message)  # Print to console for easier debugging


def close_programs():
    # Close the main program and any subprograms
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process.info['name'] in ['python.exe', 'pythonw.exe']:
                cmdline = process.info['cmdline']
                if cmdline and any(part in cmdline for part in ["mainprogram.pyw", "Programs"]):
                    log_message(f"Terminating process: {process.info['name']} with PID: {process.info['pid']}")
                    process.terminate()
                    process.wait()  # Wait for the process to terminate
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def update():
    root = tk.Tk()
    root.title("Updater")
    root.geometry("400x300")
    label = Label(root, text="Starting update...")
    label.pack(pady=20)
    root.update()
    log_message("Starting update...")

    # Close running programs
    label.config(text="Closing running programs...")
    root.update()
    log_message("Closing running programs...")
    close_programs()
    time.sleep(2)

    # Update main program
    label.config(text="Downloading main program...")
    root.update()
    log_message("Downloading main program...")
    response = requests.get(MAIN_PROGRAM_URL)
    if response.status_code == 200:
        content = response.content
        with open(MAIN_PROGRAM_PATH, 'wb') as f:
            f.write(content)
        label.config(text="Main program updated.")
        log_message("Main program updated.")
    else:
        label.config(text=f"Failed to download main program. Status code: {response.status_code}")
        log_message(f"Failed to download main program. Status code: {response.status_code}")
    root.update()
    time.sleep(1)

    # Update subprograms
    label.config(text="Downloading subprograms...")
    root.update()
    log_message("Downloading subprograms...")
    response = requests.get(GITHUB_REPO_URL)
    if response.status_code == 200:
        files = response.json()
        log_message(f"Files fetched from GitHub: {files}")

        # Clear the PROGRAMS_PATH directory
        for filename in os.listdir(PROGRAMS_PATH):
            file_path = os.path.join(PROGRAMS_PATH, filename)
            os.remove(file_path)
            log_message(f"Deleted: {file_path}")

        # Download all subprograms again
        for file in files:
            if file['type'] == 'file':
                download_url = file['download_url']
                log_message(f"Downloading from URL: {download_url}")
                response = requests.get(download_url)
                if response.status_code == 200:
                    content = response.content
                    with open(os.path.join(PROGRAMS_PATH, file['name']), 'wb') as f:
                        f.write(content)
                    log_message(f"Downloaded: {file['name']}")
                else:
                    log_message(f"Failed to download {file['name']}, status code: {response.status_code}")
    else:
        log_message(f"Failed to fetch subprograms, status code: {response.status_code}")

    time.sleep(1)
    label.config(text="Subprograms updated.")
    root.update()
    log_message("Subprograms updated.")

    label.config(text="Update complete. Please restart the main program.")
    root.update()
    log_message("Update complete. Please restart the main program.")
    root.mainloop()


if __name__ == "__main__":
    update()
