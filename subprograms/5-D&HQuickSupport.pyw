import os
import sys
from tkinter import Tk, Label
from PIL import Image, ImageTk

# Determine if running from an EXE (in the temporary folder)
if getattr(sys, 'frozen', False):
    # If running as an EXE, use the path of the temporary folder (sys._MEIPASS)
    base_path = sys._MEIPASS
else:
    # Otherwise, use the current directory
    base_path = os.path.dirname(os.path.abspath(__file__))

# Build the path to qr.png based on the base path
qr_image_path = os.path.join(base_path, 'qr.png')

# Verify if the file exists (for debugging)
if not os.path.exists(qr_image_path):
    print(f"Error: {qr_image_path} not found!")

# Now you can open qr.png using this dynamically generated path
root = Tk()
root.title("D&H QuickSupport")

# Load the QR image
qr_image = Image.open(qr_image_path)
qr_photo = ImageTk.PhotoImage(qr_image)

# Display the QR code in the GUI
qr_label = Label(root, image=qr_photo)
qr_label.pack()

root.mainloop()
