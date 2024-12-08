import json
import os
import re
import shutil
import sys
import tkinter as tk
from tkinter import messagebox
import runpy
import requests
from PIL import Image, ImageTk
import traceback
import datetime

# Constants
BASE_DIR = r"C:\devinsprograms"
SUBPROGRAMS_DIR = os.path.join(BASE_DIR, "subprograms")
TEMPDOWNLOADS_DIR = os.path.join(BASE_DIR, "tempdownloads")

GITHUB_BASE = "https://github.com/devinalonzo/myprogram"
SUBPROGRAMS_URL = GITHUB_BASE + "/tree/main/subprograms"
MAIN_URL = GITHUB_BASE + "/tree/main"
RAW_BASE = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/"

ERROR_LOG_FILE = "error_log.txt"

def log_error(e):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"----- {datetime.datetime.now()} -----\n")
        traceback.print_exc(file=f)
        f.write("\n")

class MyProgramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("My Program Launcher")

        # Detect screen resolution
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the geometry to the screen size to fill the screen
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.state('zoomed')

        # Ensure directories exist
        os.makedirs(SUBPROGRAMS_DIR, exist_ok=True)
        os.makedirs(TEMPDOWNLOADS_DIR, exist_ok=True)

        # Attempt to download icons
        self.download_resource("resources/ico.ico", os.path.join(TEMPDOWNLOADS_DIR, "ico.ico"))
        self.download_resource("resources/ico.png", os.path.join(TEMPDOWNLOADS_DIR, "ico.png"))

        icon_path = os.path.join(TEMPDOWNLOADS_DIR, "ico.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                log_error(e)

        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var, fg="white", bg="black", font=("Arial", 10))
        self.status_label.pack(side="bottom", fill="x", pady=5)

        self.update_button = tk.Button(self.main_frame, text="Update", command=self.safe_update_files,
                                       fg="white", bg="black", activebackground="black", activeforeground="white",
                                       bd=0, highlightthickness=0, font=("Arial", 12, "bold"))
        self.update_button.pack(side="bottom", pady=(5,10))

        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0, bd=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.bg_image_original = None
        self.bg_image = None
        self.groups_data = []

        # Store screen resolution as base dimensions for layout calculations
        self.base_width = screen_width
        self.base_height = screen_height

        self.GROUP_HEADERS = {}  # Will be loaded from groups.txt

        self.root.after(100, self.safe_initial_setup)

    def safe_initial_setup(self):
        try:
            self.initial_setup()
        except Exception as e:
            log_error(e)
            messagebox.showerror("Error", f"An error occurred during initial setup: {e}")

    def safe_update_files(self):
        try:
            self.update_files()
        except Exception as e:
            log_error(e)
            messagebox.showerror("Error", f"An error occurred while updating files: {e}")

    def initial_setup(self):
        if not self.check_internet():
            self.set_status("No internet connection.")
            messagebox.showwarning("No Internet", "Unable to connect to the internet.")
        else:
            # Load group headers from remote file
            self.load_group_headers()

            self.set_status("Checking for ImDone.pyw...")
            self.check_and_run_imdone()

            self.set_status("Updating background...")
            self.update_background()

            self.set_status("Checking and updating programs...")
            self.update_files()

    def check_internet(self):
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except:
            return False

    def load_group_headers(self):
        """Load group headers from the remote groups.txt file (assumed to be JSON)."""
        url = RAW_BASE + "resources/groups.txt"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                text = r.text.strip()
                self.GROUP_HEADERS = json.loads(text)  # Parse JSON
            else:
                self.GROUP_HEADERS = {}
                messagebox.showwarning("Groups", "Could not fetch group headers, using defaults.")
        except Exception as e:
            log_error(e)
            self.GROUP_HEADERS = {}
            messagebox.showwarning("Groups", "Error loading group headers, using defaults.")

    def check_and_run_imdone(self):
        try:
            r = requests.get(MAIN_URL, timeout=10)
            if r.status_code == 200 and "ImDone.pyw" in r.text:
                self.download_file("ImDone.pyw", dest_dir=TEMPDOWNLOADS_DIR, main_dir=True)
                imdone_path = os.path.join(TEMPDOWNLOADS_DIR, "ImDone.pyw")
                if os.path.exists(imdone_path):
                    self.set_status("Running ImDone.pyw...")
                    self.run_pyw_file(imdone_path)
        except Exception as e:
            log_error(e)

    def update_background(self):
        bg_path = os.path.join(TEMPDOWNLOADS_DIR, "bkgd.png")
        success = self.download_resource("resources/bkgd.png", bg_path)
        if success and os.path.exists(bg_path):
            try:
                self.bg_image_original = Image.open(bg_path)
                resized = self.bg_image_original.resize((self.base_width, self.base_height), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(resized)
                self.canvas.delete("bg")
                self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image, tags="bg")
                self.canvas.lower("bg")
            except Exception as e:
                log_error(e)

    def update_files(self):
        self.set_status("Fetching remote file list...")
        remote_files = self.get_remote_subprograms_list()
        if remote_files is None:
            self.set_status("Failed to fetch remote file list.")
            return

        # Delete all local pyw files to ensure exact match with remote
        for f in os.listdir(SUBPROGRAMS_DIR):
            if f.lower().endswith('.pyw'):
                os.remove(os.path.join(SUBPROGRAMS_DIR, f))

        # Download all remote files fresh
        self.set_status("Downloading new files...")
        for f in remote_files:
            if self.download_file(f, dest_dir=TEMPDOWNLOADS_DIR):
                src = os.path.join(TEMPDOWNLOADS_DIR, f)
                dst = os.path.join(SUBPROGRAMS_DIR, f)
                try:
                    shutil.move(src, dst)
                except Exception as e:
                    log_error(e)
                    messagebox.showerror("Error", f"Failed to move {f} to subprograms directory: {e}")

        self.set_status("Refreshing program list...")
        self.refresh_program_buttons()
        self.set_status("Update complete.")

    def get_remote_subprograms_list(self):
        try:
            r = requests.get(SUBPROGRAMS_URL, timeout=10)
            if r.status_code != 200:
                return None
            pattern = re.compile(r'title="([^"]+\.pyw)"')
            matches = pattern.findall(r.text)
            return matches
        except Exception as e:
            log_error(e)
            return None

    def download_file(self, filename, dest_dir, main_dir=False):
        if main_dir:
            url = RAW_BASE + filename
        else:
            url = RAW_BASE + "subprograms/" + filename
        dest_path = os.path.join(dest_dir, filename)
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                with open(dest_path, 'wb') as f:
                    f.write(resp.content)
                return True
        except Exception as e:
            log_error(e)
        return False

    def download_resource(self, resource_path, dest_path):
        url = RAW_BASE + resource_path
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(dest_path, 'wb') as f:
                    f.write(r.content)
                return True
        except Exception as e:
            log_error(e)
        return False

    def refresh_program_buttons(self):
        self.canvas.delete("group_item")
        pyw_files = [f for f in os.listdir(SUBPROGRAMS_DIR) if f.endswith('.pyw')]
        grouped = {}
        for py in pyw_files:
            base_name = os.path.splitext(py)[0]
            m = re.match(r"(\d+)-(.*)", base_name)
            if m:
                group = m.group(1)
                pname = m.group(2)
            else:
                group = "0"
                pname = base_name
            grouped.setdefault(group, []).append((py, pname))

        sorted_groups = sorted(grouped.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)
        self.groups_data = sorted_groups
        self.draw_groups()

    def draw_groups(self):
        w = self.base_width
        h = self.base_height
        left_margin = 0.1 * w
        right_margin = 0.1 * w
        usable_width = w - left_margin - right_margin
        cell_width = usable_width / 5.0
        cell_height = h / 2.0

        header_font_size = 20
        button_font_size = 12

        for i, (group, files) in enumerate(self.groups_data):
            row = i // 5
            col = i % 5

            cell_x_center = left_margin + col*cell_width + cell_width/2
            cell_y_center = row * cell_height + cell_height/4

            # Use the dynamic GROUP_HEADERS, fallback if not found
            group_name = self.GROUP_HEADERS.get(group, f"Group {group}")
            self.canvas.create_text(cell_x_center, cell_y_center,
                                    text=group_name,
                                    fill="#ff1a1a",
                                    font=("Impact", header_font_size, "bold"),
                                    tags="group_item")

            button_y = cell_y_center + (header_font_size * 2)
            for (pyfile, pname) in files:
                btn = tk.Button(self.canvas, text=pname,
                                fg="white", bg="black",
                                activebackground="black", activeforeground="red",
                                bd=0, highlightthickness=0,
                                font=("Arial", button_font_size, "bold"),
                                command=lambda x=pyfile: self.run_subprogram(x))
                self.canvas.create_window(cell_x_center, button_y, window=btn, anchor="n", tags="group_item")
                button_y += (button_font_size * 3)

    def run_subprogram(self, file_path):
        full_path = os.path.join(SUBPROGRAMS_DIR, file_path)
        if os.path.exists(full_path):
            try:
                self.run_pyw_file(full_path)
            except Exception as e:
                log_error(e)
                messagebox.showerror("Error", f"Error running {file_path}:\n{e}")
        else:
            messagebox.showerror("Error", f"Program {file_path} not found.")

    def run_pyw_file(self, file_path):
        try:
            runpy.run_path(file_path, run_name="__main__")
        except SystemExit as e:
            log_error(e)
            messagebox.showerror("Script Exit", f"The script {os.path.basename(file_path)} caused a system exit: {e}")
        except Exception as e:
            log_error(e)
            messagebox.showerror("Error", f"Error running {os.path.basename(file_path)}:\n{e}")

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MyProgramGUI(root)
        root.mainloop()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
