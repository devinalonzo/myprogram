import os
import tkinter as tk
from tkinter import messagebox, Button
import urllib.request
import requests
import sys
import shutil
import json
from datetime import datetime

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
PROGRAMS_PATH = "C:\DevinsProgram\Programs"


def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)


def update_subprograms():
    response = requests.get(GITHUB_REPO_URL)
    if response.status_code == 200:
        files = response.json()
        changes_made = []

        # Clear the PROGRAMS_PATH directory
        for filename in os.listdir(PROGRAMS_PATH):
            file_path = os.path.join(PROGRAMS_PATH, filename)
            os.remove(file_path)

        # Download all subprograms again
        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.pyw'):
                if download_and_update_program(file):
                    changes_made.append(f"Downloaded subprogram: {file['name']}")

        if changes_made:
            messagebox.showinfo("Update", "Subprograms updated successfully:\n" + "\n".join(changes_made))
        else:
            messagebox.showinfo("Update", "Pulled update successfully, no updates needed.")
    else:
        messagebox.showerror("Error", "Failed to fetch subprograms from GitHub.")


def download_and_update_program(file):
    local_file_path = os.path.join(PROGRAMS_PATH, file['name'])
    download_url = file['download_url']
    content = requests.get(download_url).content
    with open(local_file_path, 'wb') as f:
        f.write(content)
    return True


def update_main_program():
    content = requests.get(MAIN_PROGRAM_URL).content
    with open(__file__, 'wb') as f:
        f.write(content)
    messagebox.showinfo("Update", "Main program updated successfully. Please reopen the application.")


def program_selection():
    ensure_directories()
    update_subprograms()  # Sync programs with GitHub on startup
    root = tk.Tk()
    root.title("Devin'sssss Program")
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

    # Add a button to update subprograms
    update_subprograms_button = Button(root, text="Update Subprograms", bg="#2e3f4f", fg="white", command=update_subprograms)
    canvas.create_window(400, 500, anchor="center", window=update_subprograms_button)

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
