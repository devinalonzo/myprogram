import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import telnetlib
import threading
import datetime
import configparser

# Constants
CONFIG_FOLDER = os.path.expanduser("~/Desktop/Tank Readings")
COMMANDS = {
    "System Configuration Report": ("I10200", 16000),
    "System Revision Level Report": ("I90200", 5000),
    "DIM Software Version": ("I79000", 4000),
    "DIM String": ("I79200", 3000),
    "Priority Alarm History": ("I11100", 45000),
    "Non-priority Alarm History": ("I11200", 40000),
    "Inventory Report": ("I20100", 10000),
    "In-Tank Delivery Report": ("I20200", 125000),
    "Tank Linear Calculated Full Volume": ("I60A00", 6000),
    "Tank Manifolded Partners": ("I61200", 8000),
    "Basic Reconciliation History": ("I@A4000", 135000),
    "Basic Inventory Reconciliation Periodic \"Row\" Report (Current)": ("IC070000", 135000),
    "Basic Inventory Reconciliation Periodic \"Row\" Report (Previous)": ("IC070001", 135000),
    "BIR Meter Data Present": ("I61500", 5000),
    "BIR Meter/Tank Mapping": ("I7B100", 15000),
    "Meter Map Diagnostics": ("I@A002", 27000),
    "ASR METER EVENT HISTORY BUFFER": ("I@A200", 45000),
    "ASR Error Event History Buffer": ("I@A900", 6000),
    "DIM EVENT HISTORY BUFFER": ("I@AB00", 55000),
    "BIR/ASR METER TOTALIZERS": ("I@AA00", 27000),
    "AccuChart Calibration History": ("IB9400", 7000),
    "AccuChart Diagnostics - Calibration Status": ("I@B600", 30000),
    "TANK CALIBRATION DATA": ("I@B900", 50000),
    "Accuchart Update Scheduling": ("I61600", 6000),
    "DIM BIR MAP and Event Buffer Reset": ("S79E00149", 0),
    "CSLD Results Report": ("I25100", 7000),
    "CSLD Rate Table": ("IA5100", 240000),
    "CSLD Rate Test": ("IA5200", 8000),
    "CSLD Volume Table": ("IA5300", 20000),
    "CSLD Moving Average Table": ("IA5400", 2100000),
    "Tank Test History": ("I20700", 45000),
    "In-Tank Leak Test Results Reports": ("I20800", 18000),
    "In-Tank Delivery Report": ("I20200", 125000),
    "TANK 20 POINT VOLUMES": ("I60600", 30000),
    "Tank Chart Report": ("I21100000001", 180000),
    "0.20 GAL/HR RESULTS": ("I37300", 27000),
    "0.20 GAL/HR History": ("I37400", 15000),
    "0.20 GAL/HR PRESSURE LINE LEAK DIAGNOSTIC REPORT": ("IB8900", 52000),
    "MID TEST RESULTS": ("IB8800", 30000),
    "3.0 GAL/HR Test Results": ("IB8700", 40000),
    "0.10 GAL/HR PRESSURE LINE LEAK DIAGNOSTIC REPORT": ("IB8A00", 10000),
    "WPLLD Line Leak 3.0 GPH Test Diagnostic": ("IB8B00", 5000),
    "WPLLD Line Leak Mid-range Test Diagnostic": ("IB8C00", 5000),
    "WPLLD Line Leak 0.2 GPH Test Diagnostic": ("IB8D00", 5000),
    "WPLLD Line Leak 0.1 GPH Test Diagnostic": ("IB8E00", 5000),
    "Liquid Sensor Status Report": ("I30100", 5000),
    "Type B (3-Wire CL) Sensor Status Report": ("I34600", 5000),
    "Type A (2-Wire CL) Sensor Status Report": ("I34100", 5000),
    "Warm Start": ("S00100", 5000)
}

COMMANDS_LIST = list(COMMANDS.items())
ROWS, COLUMNS = 5, 2
BUTTONS_PER_PAGE = ROWS * COLUMNS

class PaginatedButtons:
    def __init__(self, parent, commands, execute_command_callback):
        self.parent = parent
        self.commands = commands
        self.execute_command_callback = execute_command_callback
        self.current_page = 0
        self.total_pages = (len(self.commands) + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE

        self.buttons_frame = tk.Frame(self.parent)
        self.buttons_frame.pack(expand=True, fill=tk.BOTH)

        self.navigation_frame = tk.Frame(self.parent)
        self.navigation_frame.pack(fill=tk.X)

        self.previous_button = tk.Button(
            self.navigation_frame, text="Previous", command=self.previous_page
        )
        self.previous_button.pack(side=tk.LEFT, padx=20)

        self.page_label = tk.Label(self.navigation_frame, text="")
        self.page_label.pack(side=tk.LEFT, expand=True)

        self.next_button = tk.Button(
            self.navigation_frame, text="Next", command=self.next_page
        )
        self.next_button.pack(side=tk.RIGHT, padx=20)

        self.update_page()

    def update_page(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        start_index = self.current_page * BUTTONS_PER_PAGE
        end_index = start_index + BUTTONS_PER_PAGE
        for i, (name, (command, wait_time)) in enumerate(self.commands[start_index:end_index]):
            button = tk.Button(
                self.buttons_frame,
                text=name,
                command=lambda c=command, n=name, w=wait_time: self.execute_command_callback(c, n, w),
            )
            button.grid(row=i // COLUMNS, column=i % COLUMNS, padx=10, pady=10)

        self.page_label.config(
            text=f"Page {self.current_page + 1} of {self.total_pages}"
        )
        self.previous_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page()

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_config(ip, port, site_name, site_number):
    ensure_folder(CONFIG_FOLDER)
    config = configparser.ConfigParser()
    config['Settings'] = {
        'IP_Address': ip,
        'Port': port,
        'Site_Name': site_name,
        'Site_Number': site_number
    }
    with open(os.path.join(CONFIG_FOLDER, 'config.ini'), 'w') as configfile:
        config.write(configfile)

def load_config():
    config_path = os.path.join(CONFIG_FOLDER, 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        return config['Settings']['IP_Address'], config['Settings']['Port'], config['Settings']['Site_Name'], config['Settings']['Site_Number']
    return "", "", "", ""

def execute_command(ip, port, command, name, wait_time):
    def task():
        try:
            tn = telnetlib.Telnet(ip, int(port))
            tn.write(f"\x01{command}\r".encode("ascii"))
            response = tn.read_until(b"\x03", timeout=max(wait_time // 1000, 2)).decode("ascii")
            tn.close()

            # Display response in a new window
            response_window = tk.Toplevel()
            response_window.title(f"Response for {name}")
            response_text = scrolledtext.ScrolledText(response_window, wrap=tk.WORD, width=80, height=20)
            response_text.insert(tk.END, response)
            response_text.pack(expand=True, fill=tk.BOTH)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=task).start()

def connect_and_log(ip, port, site_name, site_number, progress_bar):
    def task():
        try:
            tn = telnetlib.Telnet(ip, int(port))
            ensure_folder(os.path.join(CONFIG_FOLDER, site_name, site_number))
            timestamp = datetime.datetime.now().strftime("%d%m%Y.%H%M")
            log_file = os.path.join(CONFIG_FOLDER, site_name, site_number, f"{timestamp}.txt")

            progress_bar["maximum"] = len(COMMANDS)
            progress_bar["value"] = 0

            with open(log_file, 'w') as f:
                for i, (name, (command, wait_time)) in enumerate(COMMANDS.items()):
                    tn.write(f"\x01{command}\r".encode("ascii"))
                    response = tn.read_until(b"\x03", timeout=max(wait_time // 1000, 2)).decode("ascii")
                    f.write(f"Command: {command} ({name})\n")
                    f.write(f"Response:\n{response}\n\n")
                    progress_bar["value"] = i + 1

            tn.close()
            messagebox.showinfo("Success", "Log saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            progress_bar["value"] = 0

    threading.Thread(target=task).start()

# GUI Setup
root = tk.Tk()
root.title("Tanks Baby Tanks")
root.state('zoomed')  # Make the GUI full screen

main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill=tk.BOTH)

header_frame = tk.Frame(main_frame)
header_frame.pack(pady=20)


# Function to check if the tank test can start
def can_start_tank_test(ip, port):
    def task():
        try:
            # Connect to the tank system
            tn = telnetlib.Telnet(ip, int(port))
            tn.write(f"\x01IA5400\r".encode("ascii"))
            response = tn.read_until(b"\x03", timeout=30).decode("ascii")
            tn.close()

            # Analyze the response
            if "DISPENSE STATE: ACTIVE" in response:
                message = "No, you cannot run the test because dispensing is currently active."
            elif "MOVING AVERAGE" in response:
                # Example logic: check for volume and temperature stability
                volumes = [float(line.split()[2]) for line in response.splitlines() if line.strip() and line[0].isdigit()]
                temperatures = [float(line.split()[4]) for line in response.splitlines() if line.strip() and line[0].isdigit()]

                if max(volumes) - min(volumes) > 0.1:
                    message = "No, you cannot run the test because the tank volume is not stable."
                elif max(temperatures) - min(temperatures) > 1.0:
                    message = "No, you cannot run the test because the temperature is not stable."
                else:
                    message = "Yes, you can run the test. The tank volume and temperature are stable."

            else:
                message = "No, you cannot run the test. The response could not be analyzed."

            # Show the message
            messagebox.showinfo("Tank Test Status", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check tank test status: {e}")

    threading.Thread(target=task).start()
    
# Add the "Can I start my Tank Test?" button to the GUI
test_button = tk.Button(header_frame, text="Can I start my Tank Test?", 
                        command=lambda: can_start_tank_test(ip_entry.get(), port_entry.get()))
test_button.grid(row=6, column=0, columnspan=2, pady=10)

def on_connect_and_log():
    ip = ip_entry.get()
    port = port_entry.get()
    site_name = site_name_entry.get()
    site_number = site_number_entry.get()
    save_config(ip, port, site_name, site_number)
    connect_and_log(ip, port, site_name, site_number, progress_bar)

ip_label = tk.Label(header_frame, text="IP Address")
ip_label.grid(row=0, column=0, padx=5, pady=5)
ip_entry = tk.Entry(header_frame)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

port_label = tk.Label(header_frame, text="Port")
port_label.grid(row=1, column=0, padx=5, pady=5)
port_entry = tk.Entry(header_frame)
port_entry.grid(row=1, column=1, padx=5, pady=5)

site_name_label = tk.Label(header_frame, text="Site Name")
site_name_label.grid(row=2, column=0, padx=5, pady=5)
site_name_entry = tk.Entry(header_frame)
site_name_entry.grid(row=2, column=1, padx=5, pady=5)

site_number_label = tk.Label(header_frame, text="Site Number")
site_number_label.grid(row=3, column=0, padx=5, pady=5)
site_number_entry = tk.Entry(header_frame)
site_number_entry.grid(row=3, column=1, padx=5, pady=5)

progress_bar = ttk.Progressbar(header_frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=2, pady=10)

connect_button = tk.Button(header_frame, text="Connect and Log", command=on_connect_and_log)
connect_button.grid(row=5, column=0, columnspan=2, pady=10)

commands_frame = tk.LabelFrame(main_frame, text="Commands")
commands_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

paginated_buttons = PaginatedButtons(
    commands_frame, COMMANDS_LIST, lambda c, n, w: execute_command(ip_entry.get(), port_entry.get(), c, n, w)
)

# Load saved config
ip, port, site_name, site_number = load_config()
ip_entry.insert(0, ip)
port_entry.insert(0, port)
site_name_entry.insert(0, site_name)
site_number_entry.insert(0, site_number)

root.mainloop()
