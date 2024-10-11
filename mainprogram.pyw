import os
import requests
import tkinter as tk
from tkinter import messagebox, Button
import subprocess
import sys

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
PROGRAMS_PATH = r"C:\DevinsProgram\Programs"
UPDATER_PATH = r"C:\DevinsProgram\updater.pyw"
UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"


def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)


def download_updater():
    response = requests.get(UPDATER_URL)
    if response.status_code == 200:
        content = response.content
        with open(UPDATER_PATH, 'wb') as f:
            f.write(content)
    else:
        messagebox.showerror("Error", "Failed to download updater program. Please check your internet connection and try again.")
        return False
    return True


def update_main_program():
    if not os.path.exists(UPDATER_PATH):
        if not download_updater():
            return
    subprocess.Popen([sys.executable, UPDATER_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def program_selection():
    ensure_directories()
    root = tk.Tk()
    root.title("Devin'ssss Program")
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
