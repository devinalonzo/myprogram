import os
import tkinter as tk
from tkinter import messagebox, Button
import urllib.request
import requests
import sys

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/"
PROGRAMS_PATH = "C:\\DevinsProgram\\Programs"
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
MAIN_PROGRAM_PATH = os.path.abspath(__file__)


def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)


def sync_with_github():
    response = requests.get(GITHUB_REPO_URL)
    if response.status_code == 200:
        files = response.json()
        existing_files = set(os.listdir(PROGRAMS_PATH))
        github_files = set()
        main_program_updated = False

        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.py'):
                github_files.add(file['name'])
                if file['name'] == os.path.basename(MAIN_PROGRAM_PATH):
                    main_program_updated = download_and_update_main()
                else:
                    download_and_update_program(file)

        # Remove programs that are not in GitHub anymore
        for local_file in existing_files - github_files:
            os.remove(os.path.join(PROGRAMS_PATH, local_file))

        if main_program_updated:
            messagebox.showinfo("Update", "Main program updated. Restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            messagebox.showinfo("Update", "Programs updated successfully.")
    else:
        messagebox.showerror("Error", "Failed to fetch programs from GitHub.")


def download_and_update_program(file):
    local_file_path = os.path.join(PROGRAMS_PATH, file['name'])
    download_url = file['download_url']
    content = requests.get(download_url).content
    with open(local_file_path, 'wb') as f:
        f.write(content)


def download_and_update_main():
    content = requests.get(MAIN_PROGRAM_URL).content
    with open(MAIN_PROGRAM_PATH, 'wb') as f:
        f.write(content)
    return True


def program_selection():
    ensure_directories()
    sync_with_github()  # Sync programs with GitHub on startup
    root = tk.Tk()
    root.title("Devins TCPIP Programmer - Program Selection")
    root.geometry("800x600")
    root.configure(bg="#2e3f4f")

    # Create Canvas for custom theme and background
    canvas = tk.Canvas(root, width=800, height=600, bg="#2e3f4f")
    canvas.pack()

    # Add buttons for programs from GitHub
    programs = os.listdir(PROGRAMS_PATH)
    for idx, program_name in enumerate(programs):
        button = Button(root, text=program_name, bg="#2e3f4f", fg="white", command=lambda name=program_name: open_program(name))
        canvas.create_window(200, 150 + idx * 50, anchor="center", window=button)

    # Add a button to check for updates
    update_button = Button(root, text="Check for Updates", bg="#2e3f4f", fg="white", command=sync_with_github)
    canvas.create_window(400, 500, anchor="center", window=update_button)

    root.mainloop()


def open_program(program_name):
    program_path = os.path.join(PROGRAMS_PATH, program_name)
    if os.path.exists(program_path):
        os.startfile(program_path)
    else:
        messagebox.showinfo("Open Program", f"'{program_name}' not found. Please sync again.")


if __name__ == "__main__":
    program_selection()