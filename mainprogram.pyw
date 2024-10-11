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
MAIN_PROGRAM_PATH = os.path.abspath(__file__)
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
UPDATE_INFO_PATH = os.path.join(os.path.expanduser("~"), "DevinsProgram_update_info.json")
PROGRAMS_PATH = "C:\DevinsProgram\Programs"


def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)


def get_last_update_time():
    if os.path.exists(UPDATE_INFO_PATH):
        with open(UPDATE_INFO_PATH, 'r') as f:
            data = json.load(f)
            return data.get('main_program_last_updated')
    return None


def save_last_update_time(commit_time):
    data = {
        'main_program_last_updated': commit_time
    }
    with open(UPDATE_INFO_PATH, 'w') as f:
        json.dump(data, f)


def get_latest_commit_time():
    response = requests.get("https://api.github.com/repos/devinalonzo/myprogram/commits/main")
    if response.status_code == 200:
        commit_data = response.json()
        return commit_data['commit']['committer']['date']
    return None


def sync_with_github():
    response = requests.get(GITHUB_REPO_URL)
    if response.status_code == 200:
        files = response.json()
        existing_files = set(os.listdir(PROGRAMS_PATH))
        github_files = set()
        changes_made = []

        latest_commit_time = get_latest_commit_time()
        last_update_time = get_last_update_time()

        main_program_updated = False
        if latest_commit_time and (not last_update_time or latest_commit_time > last_update_time):
            main_program_updated = download_and_update_main()
            if main_program_updated:
                save_last_update_time(latest_commit_time)
                changes_made.append("Main program updated.")

        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.pyw'):
                github_files.add(file['name'])
                if download_and_update_program(file):
                    changes_made.append(f"Updated/Added subprogram: {file['name']}")

        # Remove programs that are not in GitHub anymore
        for local_file in existing_files - github_files:
            os.remove(os.path.join(PROGRAMS_PATH, local_file))
            changes_made.append(f"Deleted subprogram: {local_file}")

        if main_program_updated:
            messagebox.showinfo("Update", "Main program updated. Restarting...")
            os.execv(sys.executable, ['pythonw'] + sys.argv)
        else:
            if changes_made:
                messagebox.showinfo("Update", "Programs updated successfully:\n" + "\n".join(changes_made))
            else:
                messagebox.showinfo("Update", "Pulled update successfully, no updates needed.")
    else:
        messagebox.showerror("Error", "Failed to fetch programs from GitHub.")


def download_and_update_program(file):
    local_file_path = os.path.join(PROGRAMS_PATH, file['name'])
    download_url = file['download_url']
    content = requests.get(download_url).content
    if not os.path.exists(local_file_path) or content != open(local_file_path, 'rb').read():
        with open(local_file_path, 'wb') as f:
            f.write(content)
        return True
    return False


def download_and_update_main():
    content = requests.get(MAIN_PROGRAM_URL).content
    if not os.path.exists(MAIN_PROGRAM_PATH) or content != open(MAIN_PROGRAM_PATH, 'rb').read():
        with open(MAIN_PROGRAM_PATH, 'wb') as f:
            f.write(content)
        return True
    return False


def program_selection():
    ensure_directories()
    sync_with_github()  # Sync programs with GitHub on startup
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

    # Add a button to check for updates
    update_button = Button(root, text="Check for Updates", bg="#2e3f4f", fg="white", command=sync_with_github)
    canvas.create_window(400, 500, anchor="center", window=update_button)

    # Add an AnyDesk button in the top right corner
    anydesk_button = Button(root, text="AnyDesk", bg="#2e3f4f", fg="white", command=open_anydesk)
    canvas.create_window(750, 50, anchor="ne", window=anydesk_button)

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
