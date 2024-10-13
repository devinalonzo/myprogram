import os
import tkinter as tk
from tkinter import messagebox
from tkinter import Label, Button
from PIL import Image, ImageTk
import subprocess

# Helper function to resolve file paths when bundled with PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Function to open a subprogram (EXE file)
def open_subprogram(full_filename):
    subprograms_dir = resource_path("subprograms")
    full_prog_path = os.path.join(subprograms_dir, full_filename)
    
    if os.path.exists(full_prog_path):
        subprocess.Popen([full_prog_path], shell=True)
    else:
        messagebox.showerror("EXE not found", f"{full_prog_path} not found.")

# Main GUI layout
def create_gui():
    root = tk.Tk()
    root.title("My Program")
    root.state('zoomed')  # Open maximized but not fullscreen
    root.geometry("1200x700")  # Window size as requested

    # Load and display the background image
    background_image_path = resource_path("bkgd.png")
    bg_image = Image.open(background_image_path)
    bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
    bg_image_tk = ImageTk.PhotoImage(bg_image)

    background_label = Label(root, image=bg_image_tk)
    background_label.place(relwidth=1, relheight=1)

    # Columns and Button Lists
    column_titles = ["Pump", "CRIND", "Veeder-Root", "Passport", "Help/Resources"]
    column_data = {title: [] for title in column_titles}

    # Reading subprograms folder and organizing them into columns
    subprograms_dir = resource_path("subprograms")
    for filename in os.listdir(subprograms_dir):
        if filename.endswith(".exe"):
            display_name = filename[2:-4]  # Strip first 2 chars and the '.exe' extension for the button label
            if filename.startswith("1-"):
                column_data["Pump"].append((display_name, filename))  # Add both display name and full filename
            elif filename.startswith("2-"):
                column_data["CRIND"].append((display_name, filename))
            elif filename.startswith("3-"):
                column_data["Veeder-Root"].append((display_name, filename))
            elif filename.startswith("4-"):
                column_data["Passport"].append((display_name, filename))
            elif filename.startswith("5-"):
                column_data["Help/Resources"].append((display_name, filename))

    # Create buttons for each column
    for i, (col_title, programs) in enumerate(column_data.items()):
        col_label = Label(root, text=col_title, font=("Arial", 16, "bold"), bg="black", fg="red", padx=10, pady=5)
        col_label.grid(row=0, column=i, sticky="n")

        for j, (display_name, full_filename) in enumerate(programs):
            btn = Button(root, text=display_name, font=("Arial", 12), command=lambda p=full_filename: open_subprogram(p))
            btn.grid(row=j+1, column=i, padx=10, pady=5, sticky="ew")

    # Help/Resources section positioning
    help_section_row = max(len(programs) for programs in column_data.values()) + 1
    help_label = Label(root, text="Help/Resources", font=("Arial", 16, "bold"), bg="black", fg="red", padx=10, pady=5)
    help_label.grid(row=help_section_row, columnspan=4, sticky="ew")

    # Anydesk and Update buttons
    def open_anydesk():
        anydesk_path = os.path.join(os.path.expanduser("~"), "Desktop", "AnyDesk.exe")
        if os.path.exists(anydesk_path):
            subprocess.Popen([anydesk_path], shell=True)
        else:
            # Download and save it to the desktop if not found
            anydesk_url = "https://download.anydesk.com/AnyDesk.exe"
            subprocess.run(["powershell", "-command", f"Invoke-WebRequest -Uri {anydesk_url} -OutFile {anydesk_path}"])
            subprocess.Popen([anydesk_path], shell=True)

    def check_update():
        # Check for updates and download if needed
        # (Logic to compare current version with GitHub releases)
        pass

    # Buttons for Anydesk and Update
    anydesk_button = Button(root, text="AnyDesk", font=("Arial", 12), command=open_anydesk)
    update_button = Button(root, text="Update", font=("Arial", 12), command=check_update)
    
    anydesk_button.grid(row=help_section_row + 1, column=2, padx=10, pady=20, sticky="e")
    update_button.grid(row=help_section_row + 1, column=3, padx=10, pady=20, sticky="w")

    root.mainloop()

if __name__ == "__main__":
    create_gui()
