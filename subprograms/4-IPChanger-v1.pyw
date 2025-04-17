import os
import sys
import ctypes
import logging
import ipaddress
import tkinter as tk
from tkinter import ttk, messagebox
import wmi

# Logging
LOG_FILE = "ip_changer.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# IP Schemes
IP_SCHEMES = {
    "DHCP": "DHCP",
    "Omnia": {"ip": "172.20.100.198", "subnet": "255.255.255.0", "gateway": "172.20.100.254"},
    "SSOM": {"ip": "172.16.100.198", "subnet": "255.255.255.0", "gateway": "172.16.100.254"},
    "Gilbarco 10.5 Subnet": {"ip": "10.5.55.201", "subnet": "255.255.255.0", "gateway": None},
    "Veriphone": {"ip": "192.168.31.200", "subnet": "255.255.255.0", "gateway": None},
    "Applause": {"ip": "10.5.60.198", "subnet": "255.255.255.0", "gateway": "10.5.60.1"},
    "Veeder-Root": {"ip": "192.168.11.200", "subnet": "255.255.255.0", "gateway": None},
    "Manual": "Manual"
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

class ManualIPDialog(tk.Toplevel):
    def __init__(self, master, adapter):
        super().__init__(master)
        self.title("Manual IP Configuration")
        self.geometry("300x200")
        self.adapter = adapter

        self.entries = {}
        for idx, field in enumerate(["IP Address", "Subnet Mask", "Gateway"]):
            tk.Label(self, text=field).grid(row=idx, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(self, justify='center')
            entry.grid(row=idx, column=1, padx=5)
            self.entries[field] = entry

        tk.Button(self, text="Apply", command=self.apply_manual_ip, bg="#4CAF50", fg="white").grid(columnspan=2, pady=10)

    def apply_manual_ip(self):
        ip = self.entries["IP Address"].get()
        subnet = self.entries["Subnet Mask"].get()
        gateway = self.entries["Gateway"].get()

        if not validate_ip(ip) or not validate_ip(subnet):
            messagebox.showerror("Invalid IP", "Please enter valid IP/Subnet.")
            return
        try:
            self.adapter.EnableStatic(IPAddress=[ip], SubnetMask=[subnet])
            if gateway.strip():
                self.adapter.SetGateways(DefaultIPGateway=[gateway])
            else:
                self.adapter.SetGateways(DefaultIPGateway=[])
            logging.info(f"Manual IP set to {ip} / {subnet} / {gateway}")
            messagebox.showinfo("Success", f"Adapter IP set to {ip}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set manual IP:\n{e}")
            logging.error(f"Manual IP failed: {e}")

class IPChangerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IP Changer")
        self.geometry("500x400")
        self.configure(bg="#f0f0f0")
        self.wmi = wmi.WMI()
        self.adapters = []

        self.create_widgets()
        self.load_adapters()

    def create_widgets(self):
        ttk.Label(self, text="Select Network Adapter:", font=("Segoe UI", 10)).pack(pady=5)
        frame = ttk.Frame(self)
        frame.pack(pady=5)
        self.adapter_combo = ttk.Combobox(frame, width=60, state="readonly")
        self.adapter_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Refresh", command=self.load_adapters).pack(side=tk.LEFT)

        ttk.Label(self, text="Choose IP Scheme:", font=("Segoe UI", 10)).pack(pady=(15, 5))
        self.scheme_var = tk.StringVar()
        for scheme in IP_SCHEMES:
            ttk.Radiobutton(self, text=scheme, variable=self.scheme_var, value=scheme).pack(anchor='w', padx=20)

        ttk.Button(self, text="Apply Settings", command=self.apply_settings).pack(pady=10)

        self.ip_info = tk.Text(self, height=5, wrap="word", state="disabled", bg="#e6e6e6")
        self.ip_info.pack(padx=10, pady=10, fill="both", expand=True)

    def load_adapters(self):
        self.adapters = self.wmi.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        self.adapter_combo['values'] = [a.Description for a in self.adapters]
        if self.adapters:
            self.adapter_combo.current(0)
        self.update_ip_display()

    def get_selected_adapter(self):
        idx = self.adapter_combo.current()
        if idx < 0 or idx >= len(self.adapters):
            return None
        return self.adapters[idx]

    def apply_settings(self):
        adapter = self.get_selected_adapter()
        scheme = self.scheme_var.get()

        if not scheme:
            messagebox.showerror("No Scheme", "Please select an IP Scheme.")
            return
        if not adapter:
            messagebox.showerror("No Adapter", "Please select a valid adapter.")
            return

        if scheme == "DHCP":
            try:
                adapter.EnableDHCP()
                adapter.SetDNSServerSearchOrder()
                messagebox.showinfo("Success", "DHCP applied.")
                logging.info(f"{adapter.Description} set to DHCP.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set DHCP: {e}")
                logging.error(f"DHCP error: {e}")
        elif scheme == "Manual":
            ManualIPDialog(self, adapter)
        else:
            config = IP_SCHEMES[scheme]
            try:
                adapter.EnableStatic(IPAddress=[config["ip"]], SubnetMask=[config["subnet"]])
                if config["gateway"]:
                    adapter.SetGateways(DefaultIPGateway=[config["gateway"]])
                else:
                    adapter.SetGateways(DefaultIPGateway=[])
                messagebox.showinfo("Success", f"Static IP applied: {config['ip']}")
                logging.info(f"{adapter.Description} set to static IP: {config}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set IP: {e}")
                logging.error(f"Static IP error: {e}")

        self.update_ip_display()

    def update_ip_display(self):
        adapter = self.get_selected_adapter()
        if not adapter:
            return
        ip = ', '.join(adapter.IPAddress or ["Not set"])
        subnet = ', '.join(adapter.IPSubnet or ["Not set"])
        gateway = ', '.join(adapter.DefaultIPGateway or ["Not set"])

        info = f"Adapter: {adapter.Description}\nIP Address: {ip}\nSubnet Mask: {subnet}\nGateway: {gateway}"
        self.ip_info.configure(state="normal")
        self.ip_info.delete("1.0", "end")
        self.ip_info.insert("1.0", info)
        self.ip_info.configure(state="disabled")

# Elevate if not admin
if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
        sys.exit()

    app = IPChangerApp()
    app.mainloop()
