import sys
import os
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

# Function to handle closing the window
def close_window():
    root.destroy()

# Check if the temp folder path is passed as an argument
if len(sys.argv) > 1:
    temp_folder = sys.argv[1]
else:
    temp_folder = os.getcwd()  # Default to the current directory if no argument is passed

# Path to qr.png in the provided temp folder
qr_image_path = os.path.join(temp_folder, 'qr.png')

# Check if the file exists
if not os.path.exists(qr_image_path):
    print(f"Error: {qr_image_path} not found.")
    sys.exit(1)

# Create the main window
root = Tk()
root.title("D&H Quick Support")

# Load and display the QR code image
qr_image = Image.open(qr_image_path)
qr_photo = ImageTk.PhotoImage(qr_image)

qr_label = Label(root, image=qr_photo)
qr_label.pack()

# Add a button to close the window
close_button = Button(root, text="Close", command=close_window)
close_button.pack()

# Start the main GUI loop
root.mainloop()
