import os
import requests
import tkinter as tk
from tkinter import Label
import time

GITHUB_REPO_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
PROGRAMS_PATH = "C:\\DevinsProgram\\Programs"
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
    headers = {'Cache-Control': 'no-cache'}
    content = requests.get(MAIN_PROGRAM_URL, headers=headers).content
    with open(MAIN_PROGRAM_PATH, 'wb') as f:
        f.write(content)
    time.sleep(1)
    label.config(text="Main program updated.")
    root.update()

    # Update subprograms
    label.config(text="Downloading subprograms...")
    root.update()
    response = requests.get(GITHUB_REPO_URL, headers=headers)
    if response.status_code == 200:
        files = response.json()
        print("Files fetched from GitHub:", files)  # Debugging statement

        # Clear the PROGRAMS_PATH directory
        for filename in os.listdir(PROGRAMS_PATH):
            file_path = os.path.join(PROGRAMS_PATH, filename)
            os.remove(file_path)

        # Download all subprograms again
        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.pyw'):
                download_url = file['download_url']
                print("Downloading from URL:", download_url)  # Debugging statement
                response = requests.get(download_url, headers=headers)
                if response.status_code == 200:
                    content = response.content
                    with open(os.path.join(PROGRAMS_PATH, file['name']), 'wb') as f:
                        f.write(content)
                else:
                    print(f"Failed to download {file['name']}, status code: {response.status_code}")
        
        for filename in os.listdir(PROGRAMS_PATH):
            print(f"File in Programs Directory: {filename}")  # Debugging statement

    else:
        print(f"Failed to fetch subprograms, status code: {response.status_code}")
    time.sleep(1)
    label.config(text="Subprograms updated.")
    root.update()

    label.config(text="Update complete. Please restart the main program.")
    root.update()
    root.mainloop()


if __name__ == "__main__":
    update()
