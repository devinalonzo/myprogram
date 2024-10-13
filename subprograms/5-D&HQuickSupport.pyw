import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import io

def main():
    # Phone number
    phone_number = "(833) 591-5782"
    tel_number = "tel:" + phone_number.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    
    # Create the main window
    root = tk.Tk()
    root.title("D&H Quick Support")
    root.geometry("350x500")
    root.resizable(False, False)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(tel_number)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Convert the QR code image to a format Tkinter can use
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    tk_image = ImageTk.PhotoImage(Image.open(img_buffer))
    
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
