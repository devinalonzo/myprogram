import json
import os
import re
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import traceback
import datetime
import threading

# Constants
BASE_DIR = r"C:\devinsprograms"
SUBPROGRAMS_DIR = os.path.join(BASE_DIR, "subprograms")
TEMPDOWNLOADS_DIR = os.path.join(BASE_DIR, "tempdownloads")

GITHUB_BASE = "https://github.com/devinalonzo/myprogram"
SUBPROGRAMS_URL = GITHUB_BASE + "/tree/main/subprograms/exes"
RAW_BASE = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/"

LOCAL_VERSION_FILE = os.path.join(BASE_DIR, "currentversion.txt")
CURRENT_RELEASE_URL = RAW_BASE + "subprograms/CURRENTRELEASE.txt"
ERROR_LOG_FILE = "error_log.txt"

def log_error(e=None, message=""):
    """Log errors or general messages to a file."""
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"----- {datetime.datetime.now()} -----\n")
        if message:
            f.write(f"{message}\n")
        if e:
            traceback.print_exc(file=f)
        f.write("\n")


def read_local_version():
    """Read the local version from currentversion.txt."""
    if not os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "w") as f:
            f.write("1.0.0")
        return "1.0.0"
    with open(LOCAL_VERSION_FILE, "r") as f:
        return f.read().strip()

def write_local_version(version):
    """Write the given version to currentversion.txt."""
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(version)

class MyProgramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("My Program Launcher")

        # Initialize local version
        self.local_version = read_local_version()

        # Detect screen resolution
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the geometry to the screen size to fill the screen
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.state('zoomed')

        # Set base width and height for dynamic element placement
        self.base_width = screen_width
        self.base_height = screen_height

        # Initialize GROUP_HEADERS
        self.GROUP_HEADERS = {}

        # Ensure directories exist
        os.makedirs(SUBPROGRAMS_DIR, exist_ok=True)
        os.makedirs(TEMPDOWNLOADS_DIR, exist_ok=True)
        self.clear_temp_folder()

        # GUI setup (status bar, buttons, etc.)
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var, fg="white", bg="black", font=("Arial", 10))
        self.status_label.pack(side="bottom", fill="x", pady=5)

        self.update_button = tk.Button(self.main_frame, text="Update", command=self.safe_update_files,
                                       fg="white", bg="black", activebackground="black", activeforeground="white",
                                       bd=0, highlightthickness=0, font=("Arial", 12, "bold"))
        self.update_button.pack(side="bottom", pady=(5, 10))

        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0, bd=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.root.after(100, self.safe_initial_setup)

    def set_status_thread_safe(self, msg):
        """Update the status bar message safely from threads."""
        self.root.after(0, lambda: self.status_var.set(msg))

    def safe_update_files(self):
        def run_update():
            try:
                self.update_files()
            except Exception as e:
                log_error(e, "Error while updating files.")
                self.root.after(0, lambda: messagebox.showerror("Error", "An error occurred while updating files."))
        threading.Thread(target=run_update, daemon=True).start()

    def clear_temp_folder(self):
        """Clear the temporary downloads folder."""
        if os.path.exists(TEMPDOWNLOADS_DIR):
            shutil.rmtree(TEMPDOWNLOADS_DIR)
        os.makedirs(TEMPDOWNLOADS_DIR, exist_ok=True)

    def safe_initial_setup(self):
        try:
            self.initial_setup()
        except Exception as e:
            log_error(e, "Error during initial setup.")
            messagebox.showerror("Error", f"An error occurred during initial setup: {e}")

    def initial_setup(self):
        """Perform initial setup tasks for the application."""
        try:
            if not self.check_internet():
                self.set_status_thread_safe("No internet connection.")
                messagebox.showwarning("No Internet", "Unable to connect to the internet.")
            else:
                self.load_group_headers()
                self.check_and_run_imdone()

                # Check version and update if necessary
                if self.check_version():
                    self.update_files()

            # Ensure subprograms are loaded into the GUI
            self.refresh_program_buttons()
            self.update_background()
        except Exception as e:
            log_error(e, "Error during initial setup.")
            self.set_status_thread_safe("Initialization failed.")

    def check_version(self):
        """Check the program version against the remote version."""
        try:
            self.set_status_thread_safe("Checking for updates...")
            response = requests.get(CURRENT_RELEASE_URL, timeout=10)
            if response.status_code == 200:
                remote_version = response.text.strip()
                if self.is_newer_version(remote_version, self.local_version):
                    self.set_status_thread_safe(f"New version available: {remote_version}. Updating...")
                    self.clear_program_directory()  # Clear only if a new version is detected
                    self.update_files()
                    write_local_version(remote_version)  # Save the new version locally after a successful update
                    self.local_version = remote_version  # Update the in-memory version
                else:
                    self.set_status_thread_safe(f"Program is up to date. Version: {self.local_version}")
            else:
                self.set_status_thread_safe("Failed to check for updates.")
        except requests.exceptions.RequestException as e:
            log_error(e, "Error checking version.")
            self.set_status_thread_safe("Error checking for updates.")

    def is_newer_version(self, remote_version, local_version):
        """Compare two version strings."""
        remote_parts = [int(part) for part in remote_version.split(".")]
        local_parts = [int(part) for part in local_version.split(".")]

        for remote, local in zip(remote_parts, local_parts):
            if remote > local:
                return True
            elif remote < local:
                return False
        return len(remote_parts) > len(local_parts)

    def check_and_run_imdone(self):
        """Check for ImDone.pyw in the repository, download it, and run it if available."""
        try:
            imdone_url = RAW_BASE + "ImDone.pyw"
            imdone_path = os.path.join(TEMPDOWNLOADS_DIR, "ImDone.pyw")

            self.set_status_thread_safe("Checking for ImDone.pyw...")
            resp = requests.get(imdone_url, timeout=10)
            if resp.status_code == 200:
                with open(imdone_path, "wb") as f:
                    f.write(resp.content)

                if os.path.exists(imdone_path):
                    self.set_status_thread_safe("Running ImDone.pyw...")
                    self.run_pyw_file(imdone_path)
            else:
                self.set_status_thread_safe("ImDone.pyw not found in the repository.")
        except Exception as e:
            log_error(e)
            self.set_status_thread_safe("Error checking for ImDone.pyw.")

    def run_pyw_file(self, file_path):
        """Run a .pyw file."""
        try:
            os.system(f'start /b pythonw "{file_path}"')
        except Exception as e:
            log_error(e)
            messagebox.showerror("Error", f"Error running {os.path.basename(file_path)}:\n{e}")

    def check_internet(self):
        """Check if the internet is accessible."""
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.exceptions.RequestException:
            return False

    def load_group_headers(self):
        """Load group headers from the remote groups.txt file."""
        url = RAW_BASE + "resources/groups.txt"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                group_data = json.loads(r.text.strip())
                if isinstance(group_data, dict):  # Ensure data is a dictionary
                    self.GROUP_HEADERS.update(group_data)
                else:
                    log_error(None, "Invalid group headers format received.")
            else:
                messagebox.showwarning("Groups", "Could not fetch group headers, using defaults.")
        except Exception as e:
            log_error(e, "Error loading group headers.")
            messagebox.showwarning("Groups", "Error loading group headers, using defaults.")

    def update_background(self):
        """Update the background image of the program."""
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
        """Update the local subprogram files by downloading .exe files from the GitHub repository."""
        try:
            self.set_status_thread_safe("Fetching remote file list...")
            remote_files = self.get_remote_subprograms_list()
            if not remote_files:
                self.set_status_thread_safe("Failed to fetch remote file list.")
                return

            self.set_status_thread_safe("Downloading new files...")
            for filename in remote_files:
                dest_path = os.path.join(SUBPROGRAMS_DIR, filename)
                if not os.path.exists(dest_path):
                    if self.download_file(filename, dest_dir=SUBPROGRAMS_DIR):
                        self.set_status_thread_safe(f"Downloaded {filename}")
                    else:
                        log_error(None, f"Failed to download {filename}.")
                        self.set_status_thread_safe(f"Failed to download {filename}")
            self.refresh_program_buttons()
            self.set_status_thread_safe("Update complete.")
        except Exception as e:
            log_error(e, "Error during update process.")
            self.set_status_thread_safe("Update failed.")

    def clear_program_directory(self):
        """Clear the subprograms directory."""
        for f in os.listdir(SUBPROGRAMS_DIR):
            file_path = os.path.join(SUBPROGRAMS_DIR, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                log_error(e, f"Failed to delete {file_path}")

    def get_remote_subprograms_list(self):
        """Fetch a list of .exe files from the GitHub subprograms directory."""
        try:
            r = requests.get(SUBPROGRAMS_URL, timeout=10)
            if r.status_code != 200:
                return None
            pattern = re.compile(r'title="([^"]+\.exe)"')
            return pattern.findall(r.text)
        except requests.exceptions.RequestException as e:
            log_error(e)
            self.set_status_thread_safe("Error fetching remote file list.")
            return None

    def download_file(self, filename, dest_dir):
        """Download a file from the GitHub repository."""
        url = RAW_BASE + f"subprograms/exes/{filename}"
        dest_path = os.path.join(dest_dir, filename)
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                with open(dest_path, 'wb') as f:
                    f.write(resp.content)
                return True
        except requests.exceptions.RequestException as e:
            log_error(e)
        return False

    def download_resource(self, resource_path, dest_path):
        """Download a resource file from the GitHub repository."""
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
        """Update the GUI with buttons for each downloaded subprogram."""
        try:
            exe_files = [f for f in os.listdir(SUBPROGRAMS_DIR) if f.endswith('.exe')]

            self.canvas.delete("group_item")

            grouped = {}
            for exe in exe_files:
                base_name = os.path.splitext(exe)[0]
                m = re.match(r"(\d+)-(.*)", base_name)
                if m:
                    group = m.group(1)
                    pname = m.group(2)
                else:
                    group = "0"
                    pname = base_name
                grouped.setdefault(group, []).append((exe, pname))

            sorted_groups = sorted(grouped.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)
            self.groups_data = sorted_groups
            self.draw_groups()
        except Exception as e:
            log_error(e, "Error while refreshing program buttons.")
            self.set_status_thread_safe("Failed to refresh program list.")


    def draw_groups(self):
        """Render buttons for all subprograms on the canvas."""
        try:
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

                cell_x_center = left_margin + col * cell_width + cell_width / 2
                cell_y_center = row * cell_height + cell_height / 4

                group_name = self.GROUP_HEADERS.get(group, f"Group {group}")
                self.canvas.create_text(cell_x_center, cell_y_center,
                                        text=group_name,
                                        fill="#ff1a1a",
                                        font=("Impact", header_font_size, "bold"),
                                        tags="group_item")

                button_y = cell_y_center + (header_font_size * 2)
                for exe, pname in files:
                    btn = tk.Button(self.canvas, text=pname,
                                    fg="white", bg="black",
                                    activebackground="black", activeforeground="red",
                                    bd=0, highlightthickness=0,
                                    font=("Arial", button_font_size, "bold"),
                                    command=lambda x=exe: self.run_subprogram(x))
                    self.canvas.create_window(cell_x_center, button_y, window=btn, anchor="n", tags="group_item")
                    button_y += (button_font_size * 3)
        except Exception as e:
            log_error(e, "Error while drawing program groups.")

    def run_subprogram(self, file_path):
        """Run a downloaded .exe subprogram."""
        full_path = os.path.join(SUBPROGRAMS_DIR, file_path)
        if os.path.exists(full_path):
            try:
                os.startfile(full_path)
            except Exception as e:
                log_error(e)
                messagebox.showerror("Error", f"Error running {file_path}:\n{e}")
        else:
            log_error(f"Program {file_path} not found.")
            messagebox.showerror("Error", f"Program {file_path} not found.")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MyProgramGUI(root)
        root.mainloop()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
