import os
import re
import tkinter as tk
from tkinter import simpledialog, messagebox
import time

CURRENT_VERSION = "v0.001"

def validate_ip(ip):
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if ip_pattern.match(ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return True
    return False

def main():
    root = tk.Tk()
    root.withdraw()

    # Step 1: Get MAC address from user
    mac_address = simpledialog.askstring("TCP/IP Programmer", "Enter the MAC address (e.g., AA-BB-CC-DD-EE-FF):").strip()
    if not mac_address:
        messagebox.showerror("Error", "MAC address is required.")
        return

    # Step 2: Get IP address and gateway from user
    ip_address = simpledialog.askstring("TCP/IP Programmer", "Enter the IP address to program (e.g., 192.168.1.21):").strip()
    if not ip_address or not validate_ip(ip_address):
        messagebox.showerror("Error", "Invalid IP address format. Please enter a valid IP address.")
        return

    if not messagebox.askyesno("Confirm IP", f"Are you sure this is the IP you want to set: {ip_address}?"):
        messagebox.showinfo("Restart", "Restarting from the beginning...")
        main()
        return

    gateway = simpledialog.askstring("TCP/IP Programmer", "Enter the gateway IP address (e.g., 192.168.1.1):").strip()
    if not gateway or not validate_ip(gateway):
        messagebox.showerror("Error", "Invalid gateway IP address format. Please enter a valid IP address.")
        return

    # Step 3: Program laptop IP (manual step; reminder to user)
    messagebox.showinfo("TCP/IP Programmer", "Please set your laptop IP to a different one from the above (e.g., 192.168.1.20) with subnet mask 255.255.255.0 and no gateway.")

    # Step 4: Connect Ethernet cable (manual step; reminder to user)
    messagebox.showinfo("TCP/IP Programmer", "Connect an Ethernet cable from your laptop to the TCP/IP card.")

    # Step 5: Add ARP entry
    arp_command = f"arp -s {ip_address} {mac_address}"
    if messagebox.askyesno("TCP/IP Programmer", f"Execute ARP command?\n\n{arp_command}"):
        os.system(arp_command)
    else:
        messagebox.showinfo("TCP/IP Programmer", "ARP command skipped.")

    # Step 6: Telnet to port 1
    messagebox.showinfo("TCP/IP Programmer", "Testing connection to the card via telnet on port 1...")
    telnet_command = f"telnet {ip_address} 1"
    os.system(telnet_command)
    time.sleep(2)

    # Step 7: Telnet to port 9999
    messagebox.showinfo("TCP/IP Programmer", "Connecting to the card via telnet on port 9999...")
    telnet_command = f"telnet {ip_address} 9999"
    os.system(telnet_command)
    messagebox.showinfo("TCP/IP Programmer", "After you finish programming sections 0 (and 1 if needed), press OK to continue...")

    # Step 11: Telnet to port 10001
    messagebox.showinfo("TCP/IP Programmer", "Connecting to the card via telnet on port 10001...")
    telnet_command = f"telnet {ip_address} 10001"
    os.system(telnet_command)

    # Step 13: Send inventory command
    messagebox.showinfo("TCP/IP Programmer", "Press Ctrl + A, then type 200 to see the inventory levels.")

if __name__ == "__main__":
    main()
