import os
import sys
from tkinter import Tk, Label, Button, PhotoImage, messagebox
from PIL import Image, ImageTk
import logging

# Define the path where the files are unpacked (C:\DevinsFolder)
DEVINS_FOLDER_PATH = r"C:\DevinsFolder"

# Ensure the logging folder exists
LOG_FILE_PATH = os.path.join(DEVINS_FOLDER_PATH, "quick_support.log")
os.makedirs(DEVINS_FOLDER_PATH, exist_ok=True)

# Set up logging
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to get file paths from C:\DevinsFolder
def get_devins_folder_path(filename):
    return os.path.join(DEVINS_FOLDER_PATH, filename)

# Define the image and icon paths using the DEVINS_FOLDER_PATH
QR_IMAGE_PATH = get_devins_folder_path("qr.png")  # Ensure the QR image is placed here
ICON_IMAGE_PATH = get_devins_folder_path("ico.png")

# Function to start the program
def start_quick_support():
    root = Tk()
    root.title("Quick Support")

    # Try to load the icon image for the window
    try:
        root.iconphoto(True, PhotoImage(file=ICON_IMAGE_PATH))
    except Exception as e:
        logging.error(f"Error loading icon image: {e}")
        messagebox.showerror("Error", f"Icon image not found: {e}")

    # Set the window size
    root.geometry("400x300")
    root.minsize(400, 300)

    # Try to load the QR code image
    try:
        qr_image = Image.open(QR_IMAGE_PATH)
        qr_photo = ImageTk.PhotoImage(qr_image)
        qr_label = Label(root, image=qr_photo)
        qr_label.image = qr_photo  # Keep a reference to avoid garbage collection
        qr_label.pack(pady=20)
    except FileNotFoundError:
        logging.error(f"QR image not found: {QR_IMAGE_PATH}")
        messagebox.showerror("Error", f"QR image not found at {QR_IMAGE_PATH}")
    except Exception as e:
        logging.error(f"Error loading QR image: {e}")
        messagebox.showerror("Error", f"Error loading QR image: {e}")

    # Add a label with instructions
    instruction_label = Label(root, text="Scan this QR code for Quick Support", font=("Helvetica", 14))
    instruction_label.pack(pady=10)

    # Button to close the window
    close_button = Button(root, text="Close", command=root.destroy)
    close_button.pack(pady=10)

    # Display the window
    root.mainloop()

if __name__ == "__main__":
    logging.info("Starting Quick Support")
    start_quick_support()
