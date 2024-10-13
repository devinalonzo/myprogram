import os
import subprocess
import tkinter as tk
from tkinter import messagebox, Button
from PIL import Image, ImageTk

# Helper function to resolve paths
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller bundled files """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Set the correct paths for programs and resources
PROGRAMS_PATH = resource_path('subprograms')
BACKGROUND_PATH = resource_path('bkgd.png')

# Open a selected program from the EXE folder instead of .pyw files
def open_program(program_name):
    exe_name = os.path.splitext(program_name)[0] + ".exe"  # Look for the EXE version
    program_path = resource_path(os.path.join('subprograms', exe_name))  # Ensure EXE path
    
    if os.path.exists(program_path):
        subprocess.Popen([program_path], shell=True)
    else:
        messagebox.showinfo("Open Program", f"'{exe_name}' not found. Please sync again.")

# Program selection UI
def program_selection():
    root = tk.Tk()
    root.title("Devin's Program")
    root.geometry("800x600")

    # Load and set background image
    background_image = Image.open(BACKGROUND_PATH)
    background_image = background_image.resize((800, 600), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Button styling
    button_bg = "#4e5d6c"
    button_fg = "#ffffff"
    button_font = ("Helvetica", 12, "bold")

    # List programs from the local directory or EXE-bundled folder
    if os.path.exists(PROGRAMS_PATH):
        programs = os.listdir(PROGRAMS_PATH)
        if programs:
            for idx, program_name in enumerate(programs):
                program_display_name = os.path.splitext(program_name)[0]
                button = Button(root, text=program_display_name, bg=button_bg, fg=button_fg, font=button_font,
                                command=lambda name=program_name: open_program(name))
                button.place(x=350, y=150 + idx * 50)
        else:
            messagebox.showinfo("No Programs Found", "No subprograms are available in the subprograms folder.")
    else:
        messagebox.showinfo("No Programs Found", "Subprograms folder not found!")

    root.mainloop()

# Run the program selection UI
if __name__ == "__main__":
    program_selection()
