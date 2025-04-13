import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import telnetlib
import threading
import datetime
import configparser
import requests
import webbrowser

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
ROWS, COLUMNS = 4, 3
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
        # Clear previous buttons
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        # Calculate the button placement
        start_index = self.current_page * BUTTONS_PER_PAGE
        end_index = start_index + BUTTONS_PER_PAGE

        # Configure grid weights for centering
        for col in range(COLUMNS):
            self.buttons_frame.grid_columnconfigure(col, weight=1)
        for row in range(ROWS):
            self.buttons_frame.grid_rowconfigure(row, weight=1)

        # Add buttons
        for i, (name, (command, wait_time)) in enumerate(self.commands[start_index:end_index]):
            button = tk.Button(
                self.buttons_frame,
                text=name,
                command=lambda c=command, n=name, w=wait_time: self.execute_command_callback(c, n, w),
                width=20,  # Specify a fixed width if desired
                height=1   # Specify a fixed height if desired
            )
            button.grid(
                row=i // COLUMNS, column=i % COLUMNS, padx=10, pady=10, sticky="nsew"
            )

        # Update the navigation
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

# def execute_command(ip, port, command, name, wait_time):
    # def task():
        # try:
            # tn = telnetlib.Telnet(ip, int(port))
            # tn.write(f"\x01{command}\r".encode("ascii"))
            # response = tn.read_until(b"\x03", timeout=max(wait_time // 1000, 2)).decode("ascii")
            # tn.close()

            # formatted_response = []
            # for line in response.splitlines():
                # if line.strip() and len(line.split()) > 0:
                    # try:
                        # time_field = line.split()[0]
                        # if len(time_field) == 12 and time_field.isdigit():
                            # readable_time = datetime.datetime.strptime(time_field, "%y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                            # line = line.replace(time_field, readable_time, 1)
                    # except Exception as e:
                        # pass  # Leave line unmodified if parsing fails
                # formatted_response.append(line)

            # formatted_response_str = "\n".join(formatted_response)

            # response_window = tk.Toplevel()
            # response_window.title(f"Response for {name}")
            # response_text = scrolledtext.ScrolledText(response_window, wrap=tk.WORD, width=80, height=20)
            # response_text.insert(tk.END, formatted_response_str)
            # response_text.pack(expand=True, fill=tk.BOTH)
        # except Exception as e:
            # messagebox.showerror("Error", str(e))

    # threading.Thread(target=task).start()






def execute_command(ip, port, command, name, wait_time):
    """
    Executes a command and updates the progress bar.
    """
    def task():
        try:
            # Update progress bar to indicate the start
            progress_bar["value"] = 0
            progress_bar["maximum"] = 1
            
            tn = telnetlib.Telnet(ip, int(port))
            tn.write(f"\x01{command}\r".encode("ascii"))
            response = tn.read_until(b"\x03", timeout=max(wait_time // 1000, 2)).decode("ascii")
            tn.close()

            # Process the response
            formatted_response = []
            for line in response.splitlines():
                if line.strip() and len(line.split()) > 0:
                    try:
                        # Reformat time in response
                        time_field = line.split()[0]
                        if len(time_field) == 12 and time_field.isdigit():
                            readable_time = datetime.datetime.strptime(time_field, "%y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                            line = line.replace(time_field, readable_time, 1)
                    except Exception:
                        pass
                formatted_response.append(line)

            formatted_response_str = "\n".join(formatted_response)

            # Display response in a new window
            response_window = tk.Toplevel()
            response_window.title(f"Response for {name}")
            response_text = scrolledtext.ScrolledText(response_window, wrap=tk.WORD, width=80, height=20)
            response_text.insert(tk.END, formatted_response_str)
            response_text.pack(expand=True, fill=tk.BOTH)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            # Mark the progress as complete
            progress_bar["value"] = 1

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
root.title("Tank Logger")
root.state('zoomed')  # Make the GUI full screen

main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill=tk.BOTH)

header_frame = tk.Frame(main_frame)
header_frame.pack(pady=20)


def can_start_tank_test(ip, port):
    """
    Checks if the tank test can start and updates the progress bar.
    """
    def task():
        try:
            # Initialize progress bar
            progress_bar["value"] = 0
            progress_bar["maximum"] = 1
            
            # Connect to the tank system
            tn = telnetlib.Telnet(ip, int(port))
            progress_bar["value"] += 0.5  # Increment progress after connection
            
            tn.write(f"\x01IA5400\r".encode("ascii"))
            response = tn.read_until(b"\x03", timeout=30).decode("ascii")
            tn.close()
            progress_bar["value"] += 0.5  # Increment progress after receiving response

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
        finally:
            progress_bar["value"] = progress_bar["maximum"]  # Ensure progress is complete

    threading.Thread(target=task).start()
    
# Add the "Can I start my Tank Test?" button to the GUI
test_button = tk.Button(header_frame, text="Can I start a SLD (Static Leak Detection) Test?", 
                        command=lambda: can_start_tank_test(ip_entry.get(), port_entry.get()))
test_button.grid(row=6, column=0, columnspan=2, pady=10)



def analyze_full_csld(ip, port):
    """
    Comprehensive CSLD analysis covering all document conditions with detailed data for each issue.
    Includes progress bar updates.
    """
    def task():
        try:
            # Initialize progress bar
            progress_bar["value"] = 0
            progress_bar["maximum"] = len(COMMANDS) + 1  # +1 for the final log and display step
            
            tn = telnetlib.Telnet(ip, int(port))

            # Fetch all reports required for the full analysis
            reports = {}
            for i, (name, (command, wait_time)) in enumerate(COMMANDS.items(), start=1):
                tn.write(f"\x01{command}\r".encode("ascii"))
                response = tn.read_until(b"\x03", timeout=max(wait_time // 1000, 2)).decode("ascii")
                reports[name] = response

                # Update progress bar after each command
                progress_bar["value"] = i

            tn.close()

            # Begin comprehensive analysis
            analysis = []

            # Phase 1: Pre-conditions (Idle, Stability)
            if "DISPENSE STATE: ACTIVE" in reports["CSLD Moving Average Table"]:
                analysis.append("Tank is not idle. Data: DISPENSE STATE: ACTIVE detected in Moving Average Table.")

            volumes = [
                float(line.split()[2]) for line in reports["CSLD Moving Average Table"].splitlines()
                if line.strip() and line[0].isdigit()
            ]
            if max(volumes) - min(volumes) > 0.1:
                analysis.append(f"Volume fluctuations detected. Data: Max Volume = {max(volumes)}, Min Volume = {min(volumes)}.")

            temperatures = [
                float(line.split()[4]) for line in reports["CSLD Moving Average Table"].splitlines()
                if line.strip() and line[0].isdigit()
            ]
            if max(temperatures) - min(temperatures) > 1.0:
                analysis.append(f"Temperature fluctuations detected. Data: Max Temp = {max(temperatures)}, Min Temp = {min(temperatures)}.")

            # Phase 2: Test Execution (Duration, Leak Rates)
            if "TEST DURATION" in reports["CSLD Rate Test"]:
                test_duration = float(reports["CSLD Rate Test"].split("TEST DURATION:")[1].split()[0])
                if test_duration < 28:
                    analysis.append(f"Test duration insufficient. Data: TEST DURATION = {test_duration} minutes.")
            else:
                analysis.append("Test duration data missing. Data: No TEST DURATION field found in Rate Test report.")

            if "leak rate < +0.4 gph" not in reports["CSLD Results Report"]:
                leak_rate_lines = [line for line in reports["CSLD Results Report"].splitlines() if "LEAK RATE" in line]
                analysis.append(f"Leak rate exceeds acceptable threshold. Data: {'; '.join(leak_rate_lines)}")

            # Phase 3: Post-Test Analysis
            if "CSLD Volume Table must be complete" not in reports["CSLD Volume Table"]:
                analysis.append("CSLD Volume Table incomplete. Data: Volume Table report indicates missing entries.")

            # Phase 4: Hardware and Communication Diagnostics
            if "PROBE FAULT" in reports["DIM EVENT HISTORY BUFFER"]:
                fault_lines = [line for line in reports["DIM EVENT HISTORY BUFFER"].splitlines() if "PROBE FAULT" in line]
                analysis.append(f"Probe faults detected. Data: {'; '.join(fault_lines)}")

            if "COMMUNICATION ERROR" in reports["DIM EVENT HISTORY BUFFER"]:
                error_lines = [line for line in reports["DIM EVENT HISTORY BUFFER"].splitlines() if "COMMUNICATION ERROR" in line]
                analysis.append(f"Communication error detected. Data: {'; '.join(error_lines)}")

            # Advanced Scenarios (Multi-Tank, Environmental)
            if "Manifolded Tanks" in reports["Tank Linear Calculated Full Volume"]:
                analysis.append("Multi-tank system detected. Data: 'Manifolded Tanks' present in Full Volume report.")

            # Generate Compliance Log
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(CONFIG_FOLDER, f"CSLD_Analysis_{timestamp}.log")
            with open(log_file, 'w') as log:
                log.write("CSLD Comprehensive Analysis Log\n")
                log.write(f"Timestamp: {timestamp}\n\n")
                log.write("Issues Detected:\n")
                log.writelines(f"- {item}\n" for item in analysis)

            # Update progress bar for final step
            progress_bar["value"] = progress_bar["maximum"]

            # Display Results
            analysis_window = tk.Toplevel()
            analysis_window.title("CSLD Analysis")
            
            # Add completion message
            completion_label = tk.Label(
                analysis_window, 
                text=f"Analysis complete. Log saved to {log_file}", 
                fg="green", 
                font=("Arial", 12, "bold"),
                wraplength=600
            )
            completion_label.pack(pady=10)

            # Display the analysis results in a scrolled text box
            summary = f"CSLD Comprehensive Analysis:\n\nIssues Detected:\n{'\n'.join(analysis) or 'None detected.'}\n"
            text_widget = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD, width=100, height=30)
            text_widget.insert(tk.END, summary)
            text_widget.pack(expand=True, fill=tk.BOTH)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform CSLD analysis: {e}")
        finally:
            # Ensure progress bar reaches maximum on completion or error
            progress_bar["value"] = progress_bar["maximum"]

    threading.Thread(target=task).start()

    
csld_button = tk.Button(header_frame, text="CSLD Analysis", 
                        command=lambda: analyze_full_csld(ip_entry.get(), port_entry.get()))
csld_button.grid(row=9, column=0, columnspan=2, pady=10)





def ensure_folder(folder_path):
    """
    Ensure the folder exists, creating it if necessary.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def download_and_open_help_file():
    """
    Check for internet connection and download or open the help file and the PDF.
    """
    help_file_url = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/help/help.html"
    pdf_file_url = "https://raw.githubusercontent.com/devinalonzo/myprogram/main/help/CSLD.pdf"
    help_save_path = os.path.join(CONFIG_FOLDER, "help.html")
    pdf_save_path = os.path.join(CONFIG_FOLDER, "CSLD.pdf")

    def is_internet_connected():
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    if is_internet_connected():
        try:
            # Ensure the folder exists
            ensure_folder(CONFIG_FOLDER)

            # Download the HTML help file
            response = requests.get(help_file_url)
            response.raise_for_status()  # Raise error for HTTP issues
            with open(help_save_path, "wb") as file:
                file.write(response.content)

            # Download the PDF file
            response = requests.get(pdf_file_url)
            response.raise_for_status()  # Raise error for HTTP issues
            with open(pdf_save_path, "wb") as file:
                file.write(response.content)

            # Open the downloaded HTML file in a browser
            webbrowser.open(help_save_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download the files: {e}")
    else:
        # Check if the HTML file exists locally
        if os.path.exists(help_save_path):
            # Open the HTML file locally
            webbrowser.open(help_save_path)
            messagebox.showinfo("Help File", "Opened the local help file.")
        else:
            # File not available locally
            messagebox.showwarning(
                "Help File Unavailable",
                "Help file is unavailable. Please connect to the internet to download it."
            )

# Add the "Help" button to the GUI
help_button = tk.Button(root, text="Help", command=download_and_open_help_file)
help_button.place(relx=0.95, rely=0.05, anchor=tk.NE)




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

commands_frame = tk.LabelFrame(main_frame, text="Manual Commands")
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
