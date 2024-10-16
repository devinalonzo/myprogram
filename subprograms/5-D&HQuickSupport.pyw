import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Function to get the path for DevinsFolder resources
def get_devinsfolder_path(filename):
    return os.path.join('C:\\DevinsFolder', filename)

# Load the QR image from C:\DevinsFolder
try:
    qr_image_path = get_devinsfolder_path('qr.png')
    qr_image = Image.open(qr_image_path)
except FileNotFoundError:
    messagebox.showerror("Error", f"QR image not found at {qr_image_path}")
    sys.exit(1)

# Function to display the QR code
def display_qr_code():
    root = tk.Tk()
    root.title("D&H Quick Support")

    # Convert the QR image to a format Tkinter can use
    qr_photo = ImageTk.PhotoImage(qr_image)

    # Create a label to display the image
    label = tk.Label(root, image=qr_photo)
    label.pack()

    # Button to close the window
    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    display_qr_code()
