import os
import requests
import tkinter as tk
from tkinter import messagebox, Button, PhotoImage
import subprocess
import sys
from PIL import Image, ImageTk

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"
BACKGROUND_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/bkgd.png"
ANYDESK_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
PROGRAMS_PATH = r"C:\DevinsProgram\Programs"
UPDATER_PATH = r"C:\DevinsProgram\updater.pyw"
UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"
BACKGROUND_PATH = os.path.join(r"C:\DevinsProgram", "bkgd.png")


def ensure_directories():
    if not os.path.exists(PROGRAMS_PATH):
        os.makedirs(PROGRAMS_PATH)
    if not os.path.exists(os.path.dirname(BACKGROUND_PATH)):
        os.makedirs(os.path.dirname(BACKGROUND_PATH))


def download_background():
    response = requests.get(BACKGROUND_URL)
    if response.status_code == 200:
        content = response.content
        with open(BACKGROUND_PATH, 'wb') as f:
            f.write(content)
    else:
        messagebox.showerror("Error", "Failed to download background image. Please check your internet connection and try again.")
        return False
    return True


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
    if not os.path.exists(BACKGROUND_PATH):
        download_background()

    root = tk.Tk()
    root.title("Devin's Program")
    root.geometry("800x600")

    # Load the background image
    background_image = Image.open(BACKGROUND_PATH)
    background_image = background_image.resize((800, 600), Image.LANCZOS)  # Resize to fit the window
    background_photo = ImageTk.PhotoImage(background_image)

    # Set the background
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Style adjustments for readability
    button_bg = "#4e5d6c"  # Slightly lighter than background
    button_fg = "#ffffff"  # White text for contrast
    button_font = ("Helvetica", 12, "bold")

    # Add buttons for programs from GitHub
    programs = os.listdir(PROGRAMS_PATH)
    for idx, program_name in enumerate(programs):
        program_display_name = os.path.splitext(program_name)[0]  # Remove extension from button label
        button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font, command=lambda name=program_name: open_program(name))
        button.place(x=350, y=150 + idx * 50)

    # Add an AnyDesk button in the top right corner
    anydesk_button = Button(root, text="AnyDesk", bg=button_bg, fg=button_fg, font=button_font, command=open_anydesk)
    anydesk_button.place(x=650, y=20)

    # Add an Update button in the top right corner
    update_button = Button(root, text="Update", bg=button_bg, fg=button_fg, font=button_font, command=update_main_program)
    update_button.place(x=550, y=20)

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
