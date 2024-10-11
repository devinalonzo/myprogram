import tkinter as tk
from tkinter import messagebox
import subprocess
import time

class TCPIPProgrammer:
    def __init__(self, root):
        self.root = root
        self.root.title("Devin's TCPIP Programmer")
        
        # Step 1: MAC Address Input
        self.mac_label = tk.Label(root, text="Enter the card MAC address (format: xx-xx-xx-xx-xx-xx):")
        self.mac_label.pack()
        self.mac_entry = tk.Entry(root)
        self.mac_entry.pack()
        
        # Step 2: IP Address and Gateway Input
        self.ip_label = tk.Label(root, text="Enter the IP address for the card:")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(root)
        self.ip_entry.pack()
        
        self.gateway_label = tk.Label(root, text="Enter the gateway IP address:")
        self.gateway_label.pack()
        self.gateway_entry = tk.Entry(root)
        self.gateway_entry.pack()
        
        # Step 3: Laptop IP Input
        self.laptop_ip_label = tk.Label(root, text="Enter your laptop IP address (different from card IP):")
        self.laptop_ip_label.pack()
        self.laptop_ip_entry = tk.Entry(root)
        self.laptop_ip_entry.pack()
        
        # Start Button
        self.start_button = tk.Button(root, text="Start Programming", command=self.start_programming)
        self.start_button.pack()
        
        # Log Output
        self.log_text = tk.Text(root, height=15, width=50)
        self.log_text.pack()
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def start_programming(self):
        mac = self.mac_entry.get()
        ip = self.ip_entry.get()
        gateway = self.gateway_entry.get()
        laptop_ip = self.laptop_ip_entry.get()

        if not (mac and ip and gateway and laptop_ip):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        # Step 3: Configure Laptop IP
        self.log("Configuring laptop IP address...")
        # Note: You might need admin privileges to run this command
        command = f"netsh interface ip set address name=\"Ethernet\" static {laptop_ip} 255.255.255.0"
        self.log(self.run_command(command))
        
        # Step 5: ARP Command
        self.log("Adding ARP entry...")
        command = f"arp -s {ip} {mac}"
        self.log(self.run_command(command))
        
        # Step 6: Telnet to port 1
        self.log("Testing connection to the card (port 1)...")
        command = f"telnet {ip} 1"
        result = self.run_command(command)
        if "Could not open connection" in result:
            self.log("Connection test successful.")
        else:
            self.log("Error: " + result)
            self.log("Restarting process from Step 1.")
            return
        
        # Step 7: Telnet to port 9999
        self.log("Connecting to the card (port 9999)...")
        command = f"telnet {ip} 9999"
        self.log(self.run_command(command))
        time.sleep(2)
        
        # Step 8-10: Program Sections 0 and 1
        self.log("Programming section 0...")
        # Assuming manual input is required here - this part can't be fully automated without more details
        messagebox.showinfo("Manual Step", "Please complete section 0 and section 1 programming manually in the telnet session.")
        
        # Step 11: Telnet to port 10001
        self.log("Connecting to the card (port 10001)...")
        command = f"telnet {ip} 10001"
        self.log(self.run_command(command))
        
        # Step 13: Inventory Levels
        self.log("Retrieving inventory levels...")
        # Note: Sending Ctrl+A, 200 might require a different approach in an actual telnet session
        self.log("Type 'Ctrl+A, 200' in the telnet session to retrieve inventory levels.")
        
        self.log("Programming complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TCPIPProgrammer(root)
    root.mainloop()
