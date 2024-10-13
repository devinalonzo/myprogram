import os
import sys
import requests
import ctypes
import psutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# GitHub API URL for fetching subprograms
GITHUB_API_URL = "https://api.github.com/repos/devinalonzo/myprogram/contents/subprograms"

# File paths
MAIN_PROGRAM_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/mainprogram.pyw"
UPDATER_URL = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/updater.pyw"
PROGRAMS_PATH = r"C:\DevinsProgram\Programs"  # Program folder path
MAIN_PROGRAM_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'mainprogram.pyw')
UPDATER_PATH = r"C:\DevinsProgram\updater.pyw"  # Path to save updater in C:\DevinsProgram

# Ensure the DevinsProgram directory exists
if not os.path.exists(r"C:\DevinsProgram"):
    os.makedirs(r"C:\DevinsProgram")

# GUI setup
root = tk.Tk()
root.title("Updater")
root.geometry("400x200")

log_text = tk.Text(root, height=10, width=50)
log_text.pack()

progress = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress.pack(pady=10)

def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    log_text.update_idletasks()  # Ensure the log updates immediately

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_to_admin():
    """Relaunch the script with administrator privileges."""
    if not is_admin():
        log_message("Relaunching as admin...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def kill_programs():
    """Close any running Python programs named 'Devin's Program'."""
    log_message("Checking for running instances of Devin's Program...")
    found_program = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Log the process name and command line to inspect it
            log_message(f"Checking process: {proc.info['name']} with command line: {proc.info['cmdline']}")
            
            # Match based on the script name 'mainprogram.pyw' or command line containing 'Devin\'s Program'
            if proc.info['name'] == 'python.exe' and isinstance(proc.info['cmdline'], list):
                if 'mainprogram.pyw' in proc.info['cmdline'] or 'Devin\'s Program' in ' '.join(proc.info['cmdline']):
                    log_message(f"Terminating process: {proc.info['cmdline']}")
                    proc.terminate()  # Graceful termination
                    try:
                        proc.wait(5)  # Wait for 5 seconds for the process to terminate
                    except psutil.TimeoutExpired:
                        log_message(f"Force killing process: {proc.info['cmdline']}")
                        proc.kill()  # Force kill if terminate() didn't work
                    log_message(f"Process terminated: {proc.info['cmdline']}")
                    found_program = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log_message(f"Error terminating process: {e}")
    
    if not found_program:
        log_message("No running instances of Devin's Program found.")

def download_file(url, dest_path):
    """Download a file from a URL."""
    log_message(f"Downloading {url}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        log_message(f"Downloaded {dest_path}")
    else:
        log_message(f"Failed to download {url}, status code: {response.status_code}")

def get_subprogram_files():
    """Fetch the list of files in the GitHub subprograms folder."""
    log_message("Fetching file list from GitHub...")
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        files = response.json()
        return [file['name'] for file in files if file['type'] == 'file']
    else:
        log_message(f"Failed to fetch file list from GitHub, status code: {response.status_code}")
        return []

def delete_existing_files():
    """Delete all existing files in C:\\DevinsProgram\\Programs and download new subprograms."""
    log_message("Deleting existing files...")
    if os.path.exists(PROGRAMS_PATH):
        for file in os.listdir(PROGRAMS_PATH):
            file_path = os.path.join(PROGRAMS_PATH, file)
            try:
                os.remove(file_path)
                log_message(f"Deleted {file_path}")
            except Exception as e:
                log_message(f"Error deleting {file_path}: {e}")

def update_subprograms():
    r"""Delete all files in C:\DevinsProgram\Programs and download new subprograms."""
    delete_existing_files()
    
    subprogram_files = get_subprogram_files()
    if not subprogram_files:
        log_message("No files to download, aborting update.")
        return
    
    log_message("Downloading new subprograms from GitHub...")
    for idx, subprogram in enumerate(subprogram_files):
        progress['value'] = (idx + 1) / len(subprogram_files) * 100
        root.update_idletasks()
        download_file(f"https://raw.githubusercontent.com/devinalonzo/myprogram/main/subprograms/{subprogram}", os.path.join(PROGRAMS_PATH, subprogram))

    log_message("Subprograms updated successfully.")

def update_main_program():
    """Download and replace the main program."""
    kill_programs()  # Ensure logging has started before attempting to terminate any processes
    download_file(MAIN_PROGRAM_URL, MAIN_PROGRAM_PATH)

def update_updater():
    """Download and replace the updater."""
    log_message("Updating the updater...")
    download_file(UPDATER_URL, UPDATER_PATH)
    log_message("Updater successfully updated.")

def restart_main_program():
    """Start the main program."""
    subprocess.Popen(['python', MAIN_PROGRAM_PATH])

def on_finish():
    """Handler for finish button."""
    restart_main_program()
    root.quit()

def run_update_process():
    try:
        log_message("Starting update process...")
        update_main_program()
        update_subprograms()
        log_message("Main program and subprograms updated successfully.")
        
        # Confirmation dialog before proceeding with updater update
        log_message("Update phase 1 complete. Waiting for confirmation to proceed with updater.")
        messagebox.showinfo("Confirmation", "Main program and subprograms updated successfully. The updater will now update. Click OK to proceed.")
        
        # Update the updater
        update_updater()
        log_message("Updater update complete.")
        
        messagebox.showinfo("Updater", "The updater has been successfully updated.")
        
        root.quit()  # Close the current process
    except Exception as e:
        messagebox.showerror("Error", str(e))

finish_button = tk.Button(root, text="Finish", command=on_finish)
finish_button.pack(pady=10)

# Check and elevate to admin if necessary
if not is_admin():
    elevate_to_admin()

# Ensure logging is started before doing anything else
log_message("Updater started, logging initialized.")

# Run update process
run_update_process()

root.mainloop()
