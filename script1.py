import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Global variable to hold the app instance for cleanup
_app_instance = None

def create_content(parent):
    global _app_instance
    class BloodGlucoseLogger:
        def __init__(self, parent):
            self.parent = parent
            self.conn = None
            self.cursor = None
            self.init_database()

            # Entry frame
            self.entry_frame = tk.Frame(parent)
            self.entry_frame.pack(pady=10, padx=10, fill="x")

            self.number_entry = tk.Entry(self.entry_frame)
            self.number_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))

            self.submit_button = tk.Button(self.entry_frame, text="Submit", command=self.submit_number)
            self.submit_button.pack(side="right")

            # Create a canvas and a scrollbar
            self.canvas = tk.Canvas(parent)
            self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # Place the scrollbar and canvas
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            # Create a frame inside the canvas to hold the grid
            self.frame = ttk.Frame(self.canvas)
            self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

            # Bind configure and resize events
            self.frame.bind("<Configure>", self.configure_scroll_region)
            parent.winfo_toplevel().bind("<Configure>", self.on_resize)

            # Enable mouse wheel scrolling
            self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

            # Load initial entries
            self.load_entries()

        def init_database(self):
            """Initialize the database connection and create table if needed."""
            #if self.conn is None or self.conn.closed:
            if self.conn is None:
                self.conn = sqlite3.connect("numbers.db")
                self.cursor = self.conn.cursor()
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS numbers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number INTEGER,
                        timestamp TEXT
                    )
                """)
                self.conn.commit()

        def configure_scroll_region(self, event):
            """Update scroll region when frame size changes."""
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        def on_resize(self, event):
            """Update canvas and frame width on window resize."""
            canvas_width = self.parent.winfo_toplevel().winfo_width() - 20
            self.canvas.configure(width=canvas_width)
            self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

        def on_mouse_wheel(self, event):
            """Handle mouse wheel scrolling."""
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def load_entries(self):
            """Load and display entries from the database."""
            self.init_database()  # Ensure connection is open
            for widget in self.frame.winfo_children():
                widget.destroy()

            self.cursor.execute("SELECT id, number, timestamp FROM numbers ORDER BY id DESC")
            entries = self.cursor.fetchall()
            i = 1
            for entry in entries:
                entry_id, number, timestamp = entry
                # Left column
                if number < 70 or number > 180:
                    label_left = ttk.Label(self.frame, text=f"{timestamp}:   {number}", anchor="w", font=("Arial", 16), foreground="red")
                elif 70 <= number <= 140:
                    label_left = ttk.Label(self.frame, text=f"{timestamp}:   {number}", anchor="w", font=("Arial", 16), foreground="green")
                else:
                    label_left = ttk.Label(self.frame, text=f"{timestamp}:   {number}", anchor="w", font=("Arial", 16), foreground="black")
                label_left.grid(row=i, column=0, sticky="we", padx=10, pady=5)

                # Edit button
                edit_button = tk.Button(
                    self.frame, 
                    text="E", 
                    command=lambda eid=entry_id: self.edit_sugar(eid),
                    anchor="e"
                )
                edit_button.grid(row=i, column=1, sticky="e", padx=10, pady=5)

                # Delete button
                delete_button = tk.Button(
                    self.frame, 
                    text="X", 
                    command=lambda eid=entry_id: self.delete_entry(eid),
                    anchor="e"
                )
                delete_button.grid(row=i, column=2, sticky="e", padx=10, pady=5)

                i += 1

                self.frame.grid_columnconfigure(0, weight=1)
                self.frame.grid_columnconfigure(1, weight=0)
                self.frame.grid_columnconfigure(2, weight=0)

        def submit_number(self):
            """Submit a new number to the database."""
            self.init_database()
            number_text = self.number_entry.get().strip()
            try:
                number = int(number_text)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute(
                    "INSERT INTO numbers (number, timestamp) VALUES (?, ?)",
                    (number, timestamp)
                )
                self.conn.commit()
                self.number_entry.delete(0, tk.END)
                self.load_entries()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")

        def delete_entry(self, entry_id):
            """Delete an entry from the database."""
            self.init_database()
            if messagebox.askyesno("Confirm", "Delete this entry?"):
                self.cursor.execute("DELETE FROM numbers WHERE id = ?", (entry_id,))
                self.conn.commit()
                self.load_entries()

        def edit_sugar(self, entry_id):
            """Edit an existing entry."""
            self.init_database()
            popup = tk.Toplevel(self.parent)
            popup.title("Edit Integer")
            popup.geometry("200x200")
            popup.transient(self.parent)
            popup.grab_set()

            current_integer = self.cursor.execute("SELECT number FROM numbers WHERE id = ?", (entry_id,))
            current_integer = current_integer.fetchone()[0]

            tk.Label(popup, text="Enter new integer:").pack(pady=10)
            entry = tk.Entry(popup, justify="center")
            entry.pack(pady=5)
            entry.insert(0, current_integer)
            entry.focus_set()

            def submit():
                try:
                    new_value = int(entry.get())
                    self.cursor.execute("UPDATE numbers SET number = ? WHERE id = ?", (new_value, entry_id))
                    self.conn.commit()
                    popup.destroy()
                    self.load_entries()
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid integer")

            def cancel():
                popup.destroy()

            tk.Button(popup, text="Submit", command=submit).pack(pady=5)
            tk.Button(popup, text="Cancel", command=cancel).pack(pady=5)

        def cleanup(self):
            """Handle cleanup when the app closes."""
            if self.conn is not None and not self.conn.closed:
                self.conn.close()

    # Instantiate the app within the tab
    _app_instance = BloodGlucoseLogger(parent)

def cleanup():
    """Module-level cleanup function called by main.py."""
    global _app_instance
    if _app_instance is not None:
        _app_instance.cleanup()
        _app_instance = None