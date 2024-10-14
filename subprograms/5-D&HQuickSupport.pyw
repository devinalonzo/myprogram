import os
from tkinter import Tk, Label, Button, messagebox
from PIL import Image, ImageTk
import sys

# Get the temp folder path from the command-line argument
if len(sys.argv) > 1:
    temp_folder = sys.argv[1]
else:
    temp_folder = os.getcwd()  # Fallback to current folder if no argument is provided

# Define paths using the passed temp folder path
QR_IMAGE_PATH = os.path.join(temp_folder, 'qr.png')

# Create the main window
root = Tk()
root.title("D&H Quick Support")
root.geometry("400x400")

# Load and display the QR image
try:
    qr_image = Image.open(QR_IMAGE_PATH)
    qr_photo = ImageTk.PhotoImage(qr_image)
    qr_label = Label(root, image=qr_photo)
    qr_label.pack(pady=20)
except FileNotFoundError:
    messagebox.showerror("Error", f"QR image not found: {QR_IMAGE_PATH}")

# Add a close button
close_button = Button(root, text="Close", command=root.quit)
close_button.pack(pady=20)

# Run the main loop
root.mainloop()
