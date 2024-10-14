import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

def main():
    # Phone number
    phone_number = "(833) 591-5782"

    # Create the main window
    root = tk.Tk()
    root.title("D&H Quick Support")
    root.geometry("350x500")
    root.resizable(False, False)

    # Determine the path to the image file in the temporary directory
    if hasattr(sys, '_MEIPASS'):
        # If running as a PyInstaller EXE, get the temporary folder location
        temp_dir = sys._MEIPASS
    else:
        # If running as a script, use the current directory
        temp_dir = os.path.dirname(os.path.abspath(__file__))

    image_path = os.path.join(temp_dir, 'qr.png')

    # Load the QR code image
    try:
        qr_image = Image.open(image_path)
        tk_image = ImageTk.PhotoImage(qr_image)
    except FileNotFoundError:
        # Display an error message if the image is not found
        error_label = tk.Label(root, text="QR code image 'qr.png' not found.", font=("Arial", 14), fg="red")
        error_label.pack(pady=20)
        root.mainloop()
        return

    # Create and place the heading label
    heading_label = tk.Label(root, text="D&H Quick Support", font=("Arial", 18, "bold"))
    heading_label.pack(pady=20)

    # Create and place the instruction label
    instruction_label = tk.Label(root, text="Scan this QR code to call us!", font=("Arial", 14))
    instruction_label.pack(pady=10)

    # Create and place the QR code image
    qr_label = tk.Label(root, image=tk_image)
    qr_label.image = tk_image  # Keep a reference to prevent garbage collection
    qr_label.pack(pady=10)

    # Display the phone number below the QR code
    phone_label = tk.Label(root, text=phone_number, font=("Arial", 14))
    phone_label.pack(pady=10)

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
