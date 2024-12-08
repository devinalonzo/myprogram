import tkinter as tk
from tkinter import ttk, messagebox
import telnetlib
import threading
import os
import json
import time
import datetime
import pyperclip

CONFIG_FILE = "telnet_logger_config.json"
BASE_DIRECTORY = os.path.expanduser("~/Desktop/Tank Testing Reports")


def save_config(data):
    """Save input data to a configuration file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


def load_config():
    """Load input data from the configuration file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def get_unique_filename(directory, filename):
    """Generate a unique filename if a file with the same name already exists."""
    base, ext = os.path.splitext(filename)
    second_reading_filename = f"{base} - 2nd Reading{ext}"
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
    return second_reading_filename


def create_log_file(site_name, site_number, tank):
    """Create a unique log file path."""
    current_date = datetime.datetime.now().strftime("%m.%d")
    file_name = f"{current_date} - Tank {tank}.txt"

    # Create directory structure if not present
    site_path = os.path.join(BASE_DIRECTORY, site_name, site_number)
    os.makedirs(site_path, exist_ok=True)

    return os.path.join(site_path, get_unique_filename(site_path, file_name))


def send_command(ip, command):
    """Send a command to the Telnet connection and return the response."""
    try:
        tn = telnetlib.Telnet(ip, port=4004, timeout=10)
        tn.write(command.encode("ascii") + b"\n")
        time.sleep(1)
        response = tn.read_until(b"\x03", timeout=2).decode("ascii")
        tn.close()
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def show_response(command):
    """Display the response to a command in a popup window."""
    ip = ip_entry.get().strip()
    tank = tank_entry.get().strip()
    site_name = site_name_entry.get().strip()
    site_number = site_number_entry.get().strip()

    if not ip or not site_name or not site_number or not tank:
        messagebox.showerror("Input Error", "All fields must be filled out.")
        return

    # Replace {T} with the tank number in the command
    command = command.replace("{T}", tank)

    # Fetch response from the command
    response = send_command(ip, command)

    # Save the response to a log file
    log_file_path = create_log_file(site_name, site_number, tank)

    with open(log_file_path, "a") as logfile:
        logfile.write(f"Command: {command}\n")
        logfile.write("Response:\n")
        logfile.write(response + "\n\n")

    # Create a popup window
    popup = tk.Toplevel()
    popup.title(f"Response for {command}")
    response_text = tk.Text(popup, wrap=tk.WORD, width=60, height=20)
    response_text.insert(tk.END, response)
    response_text.config(state=tk.DISABLED)  # Make read-only
    response_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Add a "Copy" button
    def copy_to_clipboard():
        pyperclip.copy(response)
        messagebox.showinfo("Copied", "Response text copied to clipboard!")

    copy_button = tk.Button(popup, text="Copy", command=copy_to_clipboard)
    copy_button.pack(pady=10)


# GUI setup
root = tk.Tk()
root.title("Telnet Logger with Command Execution")

config = load_config()
ip_default = config.get("ip", "")
tank_default = config.get("tank", "")
site_name_default = config.get("site_name", "")
site_number_default = config.get("site_number", "")

# Input labels and fields
tk.Label(root, text="IP Address:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
ip_entry = tk.Entry(root, width=30)
ip_entry.insert(0, ip_default)
ip_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Tank #:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tank_entry = tk.Entry(root, width=30)
tank_entry.insert(0, tank_default)
tank_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Site Name:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
site_name_entry = tk.Entry(root, width=30)
site_name_entry.insert(0, site_name_default)
site_name_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Site #:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
site_number_entry = tk.Entry(root, width=30)
site_number_entry.insert(0, site_number_default)
site_number_entry.grid(row=3, column=1, padx=10, pady=5)

# Command Buttons
commands = [
    ("I11300", "Active Alarm Report"),
    ("I20C0{T}", "Last Delivery"),
    ("IA540{T}", "Moving Average"),
    ("IA550{T}", "In-Tank Leak Test Status Report"),
    ("I2030{T}", "In-Tank Leak Detect Report"),
    ("I2070{T}", "In-Tank Leak Test History Report"),
    ("I2080{T}", "In-Tank Leak Test Results Report"),
]

# Add Buttons
for idx, (cmd, label) in enumerate(commands, start=5):
    button = tk.Button(root, text=label, command=lambda c=cmd: show_response(c))
    button.grid(row=idx, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
