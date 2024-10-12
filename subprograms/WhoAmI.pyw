import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports

# Function to list available serial ports
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to send commands to the selected serial port
def send_serial_commands(port):
    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        ser.flush()
        
        # Serial commands as you provided
        commands = [
            "0128;", "19,1,0,0,0,0;", "19,2,0,0,0,0;", "19,3,0,0,0,0;", 
            "19,4,0,0,0,0;", "20,0,1,1,1,0;", "20,0,1,1,2,0;", # ... (add all other commands)
            "98,0,6,0,0,0;"
        ]
        
        result = ""
        for command in commands:
            ser.write((command + "\n").encode())  # Send command
            response = ser.readline().decode('utf-8').strip()  # Read response
            result += f"Sent: {command}, Received: {response}\n"

        # Display result in new window
        display_result(result)
        
        ser.close()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to communicate with the device: {e}")

# Function to display the result in a new window
def display_result(result):
    result_window = tk.Toplevel()
    result_window.title("Serial Communication Results")
    
    text_area = tk.Text(result_window, wrap="word")
    text_area.pack(expand=True, fill="both")
    text_area.insert("1.0", result)
    text_area.config(state="disabled")

# Main function to create the GUI
def main():
    root = tk.Tk()
    root.title("Serial Port Selector")
    
    tk.Label(root, text="Select Serial Port:").pack(pady=10)

    # Dropdown for available serial ports
    available_ports = list_serial_ports()
    port_var = tk.StringVar()
    port_dropdown = ttk.Combobox(root, textvariable=port_var, values=available_ports, state="readonly")
    port_dropdown.pack(pady=5)
    
    # Button to send commands
    send_button = tk.Button(root, text="Send Commands", command=lambda: send_serial_commands(port_var.get()))
    send_button.pack(pady=10)
    
    # Close button
    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
