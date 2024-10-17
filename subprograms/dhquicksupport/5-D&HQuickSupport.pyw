import os
import sys
from PIL import Image, ImageTk
import tkinter as tk
import logging

# Function to get the resource file from the temp directory
def get_resource_path(filename):
    temp_dir = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd()
    resources_folder = os.path.join(temp_dir, 'subprograms', 'dhquicksupport', 'Resources')
    return os.path.join(resources_folder, filename)

# Set up logging
LOG_FILE_PATH = os.path.join(os.getcwd(), 'quick_support_log.txt')
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting 5-D&H QuickSupport Program")

# Create the main application window
root = tk.Tk()
root.title("5-D&H QuickSupport")

# Load and set the background image (QR code or any other image)
try:
    qr_image_path = get_resource_path('qr.png')
    qr_image = Image.open(qr_image_path)
    qr_photo = ImageTk.PhotoImage(qr_image)
    qr_label = tk.Label(root, image=qr_photo)
    qr_label.pack()
    logging.info(f"Loaded image: {qr_image_path}")
except FileNotFoundError as e:
    logging.error(f"Image not found: {qr_image_path} - {e}")
    tk.messagebox.showerror("Error", f"QR image not found. Please ensure the resource file exists.")

# Create a quit button
def quit_program():
    logging.info("Quitting 5-D&H QuickSupport Program")
    root.quit()

quit_button = tk.Button(root, text="Quit", command=quit_program, width=10, height=2)
quit_button.pack(pady=20)

# Start the Tkinter main loop
root.mainloop()
