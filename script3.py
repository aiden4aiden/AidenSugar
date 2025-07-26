import tkinter as tk

def create_content(parent):
    # Create a frame to hold the content
    frame = tk.Frame(parent)
    frame.pack(expand=True, fill='both')
    # Add a label with "Hello, World!" with different styling
    label = tk.Label(frame, text="Hello, World!", font=("Times New Roman", 26), fg="red")
    label.pack(pady=20)