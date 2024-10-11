import os
import tkinter as tk
from tkinter import messagebox, Button, Label
import urllib.request
import requests
import sys
import shutil
import subprocess

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
PROGRAMS_PATH = r"C:\DevinsProgram\Programs"
UPDATED_MAIN_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "updated_mainprogram.pyw")
UPDATER_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "updater.pyw")


def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)


def create_updater():
    updater_code = f"""
import os
import requests
import tkinter as tk
from tkinter import Label
import time

GITHUB_REPO_URL = "{GITHUB_REPO_URL}"
MAIN_PROGRAM_URL = "{MAIN_PROGRAM_URL}"
PROGRAMS_PATH = "{PROGRAMS_PATH}"
MAIN_PROGRAM_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "mainprogram.pyw")


def update():
    root = tk.Tk()
    root.title("Updater")
    root.geometry("400x300")
    label = Label(root, text="Starting update...")
    label.pack(pady=20)
    root.update()

    # Update main program
    label.config(text="Downloading main program...")
    root.update()
    content = requests.get(MAIN_PROGRAM_URL).content
    with open(MAIN_PROGRAM_PATH, 'wb') as f:
        f.write(content)
    time.sleep(1)
    label.config(text="Main program updated.")
    root.update()

    # Update subprograms
    label.config(text="Downloading subprograms...")
    root.update()
    response = requests.get(GITHUB_REPO_URL)
    if response.status_code == 200:
        files = response.json()
        # Clear the PROGRAMS_PATH directory
        for filename in os.listdir(PROGRAMS_PATH):
            file_path = os.path.join(PROGRAMS_PATH, filename)
            os.remove(file_path)
        # Download all subprograms again
        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.pyw'):
                download_url = file['download_url']
                content = requests.get(download_url).content
                with open(os.path.join(PROGRAMS_PATH, file['name']), 'wb') as f:
                    f.write(content)
    time.sleep(1)
    label.config(text="Subprograms updated.")
    root.update()

    label.config(text="Update complete. Please restart the main program.")
    root.update()
    root.mainloop()


if __name__ == "__main__":
    update()
    """
    with open(UPDATER_PATH, 'w') as f:
        f.write(updater_code)


def update_main_program():
    create_updater()
    subprocess.Popen([sys.executable, UPDATER_PATH])
    sys.exit()


def program_selection():
    ensure_directories()
    root = tk.Tk()
    root.title("Devin'ss Program")
    root.geometry("800x600")
    root.configure(bg="#2e3f4f")

    # Create Canvas for custom theme and background
    canvas = tk.Canvas(root, width=800, height=600, bg="#2e3f4f")
    canvas.pack()

    # Add buttons for programs from GitHub
    programs = os.listdir(PROGRAMS_PATH)
    for idx, program_name in enumerate(programs):
        program_display_name = os.path.splitext(program_name)[0]  # Remove extension from button label
        button = Button(root, text=program_display_name, bg="#2e3f4f", fg="white", command=lambda name=program_name: open_program(name))
        canvas.create_window(200, 150 + idx * 50, anchor="center", window=button)

    # Add an AnyDesk button in the top right corner
    anydesk_button = Button(root, text="AnyDesk", bg="#2e3f4f", fg="white", command=open_anydesk)
    canvas.create_window(750, 50, anchor="ne", window=anydesk_button)

    # Add an Update button in the top right corner
    update_button = Button(root, text="Update", bg="#2e3f4f", fg="white", command=update_main_program)
    canvas.create_window(650, 50, anchor="ne", window=update_button)

    root.mainloop()


def open_program(program_name):
    program_path = os.path.join(PROGRAMS_PATH, program_name)
    if os.path.exists(program_path):
        os.startfile(program_path)
    else:
        messagebox.showinfo("Open Program", f"'{program_name}' not found. Please sync again.")


def open_anydesk():
    if not os.path.exists(ANYDESK_PATH):
        content = requests.get(ANYDESK_DOWNLOAD_URL).content
        with open(ANYDESK_PATH, 'wb') as f:
            f.write(content)
    os.startfile(ANYDESK_PATH)


if __name__ == "__main__":
    program_selection()
