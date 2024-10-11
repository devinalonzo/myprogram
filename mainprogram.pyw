def create_updater():
    updater_code = f"""
import os
import requests
import tkinter as tk
from tkinter import Label
import time

GITHUB_REPO_URL = "{GITHUB_REPO_URL}"
MAIN_PROGRAM_URL = "{MAIN_PROGRAM_URL}"
PROGRAMS_PATH = r"{PROGRAMS_PATH}"
MAIN_PROGRAM_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "mainprogram.pyw")
LOG_FILE_PATH = r"{LOG_FILE_PATH}"


def log_message(message):
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(f"{message}
")
    print(message)  # Print to console for easier debugging


def update():
    root = tk.Tk()
    root.title("Updater")
    root.geometry("400x300")
    label = Label(root, text="Starting update...")
    label.pack(pady=20)
    root.update()
    log_message("Starting update...")

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
    """
    with open(UPDATER_PATH, 'w') as f:
        f.write(updater_code)
    with open(UPDATER_PATH, 'w') as f:
        f.write(updater_code)


def update_main_program():
    create_updater()
    subprocess.Popen([sys.executable, UPDATER_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.exit()


def program_selection():
    ensure_directories()
    root = tk.Tk()
    root.title("Devin's Program")
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
