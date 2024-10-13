import os
import sys
import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

# Constants for GitHub release comparison
GITHUB_RELEASES_URL = "https://api.github.com/repos/devinalonzo/myprogram/releases/latest"
TEMP_DIR = getattr(sys, '_MEIPASS', os.path.abspath("."))

class DevinsProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("Devins Program")
        self.root.state('zoomed')  # Maximized window but not full-screen

        # Load background image
        self.background_image_path = os.path.join(TEMP_DIR, 'bkgd.png')
        self.set_background()

        # Set up columns and buttons
        self.setup_columns()

        # Version and action buttons (bottom right)
        self.version = "1.0.0"  # Example version, this should be set dynamically during build
        self.setup_version_and_action_buttons()

    def set_background(self):
        try:
            image = Image.open(self.background_image_path)
            background_image = ImageTk.PhotoImage(image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.ANTIALIAS))
            background_label = tk.Label(self.root, image=background_image)
            background_label.image = background_image
            background_label.place(relwidth=1, relheight=1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background: {e}")

    def setup_columns(self):
        columns_frame = tk.Frame(self.root, bg='white')
        columns_frame.place(relx=0, rely=0, relwidth=1, relheight=0.5)

        column_titles = ["Pump", "CRIND", "Veeder-Root", "Passport"]
        for idx, title in enumerate(column_titles):
            column_frame = tk.Frame(columns_frame, bd=2, relief="groove")
            column_frame.place(relx=idx * 0.25, rely=0, relwidth=0.25, relheight=1)
            label = tk.Label(column_frame, text=title, font=("Helvetica", 18, "bold"))
            label.pack(pady=10)
            self.add_buttons_to_column(column_frame, idx + 1)

    def add_buttons_to_column(self, column_frame, column_id):
        subprograms_dir = os.path.join(TEMP_DIR, "subprograms")
        if os.path.exists(subprograms_dir):
            for file in os.listdir(subprograms_dir):
                if file.startswith(f"{column_id}-") and file.endswith(".exe"):
                    button_label = file[2:].replace(".exe", "")
                    button = tk.Button(column_frame, text=button_label, command=lambda f=file: self.open_subprogram(f))
                    button.pack(pady=5, fill='x')

    def open_subprogram(self, filename):
        subprogram_path = os.path.join(TEMP_DIR, "subprograms", filename)
        os.system(f'"{subprogram_path}"')

    def setup_version_and_action_buttons(self):
        actions_frame = tk.Frame(self.root, bg='white')
        actions_frame.place(relx=0.75, rely=0.9, relwidth=0.25, relheight=0.1)

        version_label = tk.Label(actions_frame, text=f"Version: {self.version}", font=("Helvetica", 12))
        version_label.grid(row=0, column=0, padx=10, pady=5)

        update_button = tk.Button(actions_frame, text="Update", command=self.check_for_updates)
        update_button.grid(row=0, column=1, padx=10, pady=5)

        anydesk_button = tk.Button(actions_frame, text="Anydesk", command=self.open_or_download_anydesk)
        anydesk_button.grid(row=0, column=2, padx=10, pady=5)

    def check_for_updates(self):
        try:
            response = requests.get(GITHUB_RELEASES_URL)
            if response.status_code == 200:
                latest_version = response.json()["tag_name"].strip("v")
                if self.version < latest_version:
                    # Download latest release
                    release_asset_url = response.json()["assets"][0]["browser_download_url"]
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                    release_filename = release_asset_url.split("/")[-1]
                    save_path = os.path.join(desktop_path, release_filename)
                    with requests.get(release_asset_url, stream=True) as r:
                        with open(save_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    messagebox.showinfo("Update", f"Downloaded latest version to: {save_path}")
                else:
                    messagebox.showinfo("Update", "No update needed, you are on the current version.")
            else:
                messagebox.showerror("Error", "Failed to check for updates.")
        except Exception as e:
            messagebox.showerror("Error", f"Error checking for updates: {e}")

    def open_or_download_anydesk(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        anydesk_path = os.path.join(desktop_path, "AnyDesk.exe")
        if os.path.exists(anydesk_path):
            os.system(f'"{anydesk_path}"')
        else:
            try:
                anydesk_download_url = "https://download.anydesk.com/AnyDesk.exe"
                with requests.get(anydesk_download_url, stream=True) as r:
                    with open(anydesk_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                os.system(f'"{anydesk_path}"')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download AnyDesk: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DevinsProgram(root)
    root.mainloop()
