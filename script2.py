import tkinter as tk
from tkinter import simpledialog, Menu
import os
import json
import sqlite3
from datetime import datetime
import threading
import time

def create_content(parent):
    global _app_instance
    class WaterIntakeApp:
        def __init__(self, parent):
            self.parent = parent
            self.sum_total = 0
            self.buttons = []
            self.default_amount = self.load_default_amount()
            self.auto_save_interval = 5  # Default 5 minutes
            self.running = True

            # Initialize SQLite database
            self.conn = sqlite3.connect("water_intake.db")
            self.create_table()

            # Load sum_total from database
            self.load_sum_total()

            # Create menu bar (attached to parent, not root)
            self.menubar = Menu(parent)
            self.settings_menu = Menu(self.menubar, tearoff=0)
            self.settings_menu.add_command(label="Set Default Amount", command=self.set_default_amount)
            #self.settings_menu.add_command(label="Set Auto-Save Interval (minutes)", command=self.set_auto_save_interval)
            self.settings_menu.add_command(label="Save Now", command=self.save_to_db)
            self.menubar.add_cascade(label="Settings", menu=self.settings_menu)
            parent.winfo_toplevel().config(menu=self.menubar)

            # Frame for plus, minus, and default buttons
            self.button_frame = tk.Frame(parent)
            self.button_frame.pack(pady=10)

            # Create and place the "+" button
            self.add_button = tk.Button(self.button_frame, text="Add a new bottle", command=self.add_new_button)
            self.add_button.pack(side=tk.LEFT, padx=5)

            # Create and place the "-" button
            self.subtract_button = tk.Button(self.button_frame, text="Subtract amount", command=self.subtract_amount)
            self.subtract_button.pack(side=tk.LEFT, padx=5)
            """
            # Create and place the default amount button
            self.default_button = tk.Button(self.button_frame, text=f"{self.default_amount}", 
                                          command=lambda: self.add_default_button(self.default_amount))
            self.default_button.pack(side=tk.LEFT, padx=5)
            """
            # Label to display sum_total
            self.total_label = tk.Label(parent, text=f"Total Intake: {self.sum_total} ml")
            self.total_label.pack(side=tk.BOTTOM, pady=10)
            
            # Create and place the "Correct" button
            self.subtract_button = tk.Button(parent, text="Correct amount", command=self.correct_amount)
            self.subtract_button.pack(side=tk.BOTTOM, pady=10)

            # Load saved buttons
            self.load_buttons()

            # Start auto-save thread (commented out to avoid threading issues in tabbed context)
            # self.auto_save_thread = threading.Thread(target=self.auto_save, daemon=True)
            # self.auto_save_thread.start()

        def create_table(self):
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_water_intake (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    sum_total INTEGER NOT NULL
                )
            ''')
            self.conn.commit()

        def load_sum_total(self):
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = self.conn.cursor()
            cursor.execute("SELECT sum_total, date FROM daily_water_intake ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            if result and result[1] == today:
                self.sum_total = result[0]
            else:
                self.sum_total = 0

        def save_to_db(self):
            self.conn = sqlite3.connect("water_intake.db")
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM daily_water_intake WHERE date = ?", (today,))
            result = cursor.fetchone()
            if result:
                cursor.execute("UPDATE daily_water_intake SET sum_total = ? WHERE date = ?", 
                              (self.sum_total, today))
            else:
                cursor.execute("INSERT INTO daily_water_intake (date, sum_total) VALUES (?, ?)", 
                              (today, self.sum_total))
            self.conn.commit()
            """
        def auto_save(self):
            while self.running:
                self.save_to_db()
                time.sleep(self.auto_save_interval * 60)
                """
        def load_default_amount(self):
            try:
                with open("config.cfg", "r") as file:
                    return int(file.read().strip())
            except (FileNotFoundError, ValueError):
                return 400

        def save_default_amount(self, amount):
            with open("config.cfg", "w") as file:
                file.write(str(amount))

        def set_default_amount(self):
            amount = simpledialog.askinteger("Settings", "Enter default water amount (ml):", 
                                           parent=self.parent, minvalue=1, initialvalue=self.default_amount)
            if amount:
                self.default_amount = amount
                self.save_default_amount(amount)
                self.default_button.config(text=f"{self.default_amount}")
                """
        def set_auto_save_interval(self):
            interval = simpledialog.askinteger("Settings", "Enter auto-save interval (minutes):", 
                                             parent=self.parent, minvalue=1, initialvalue=self.auto_save_interval)
            if interval:
                self.auto_save_interval = interval
                """

        def load_buttons(self):
            try:
                with open("buttons.json", "r") as file:
                    data = json.load(file)
                    for btn_data in data.get("buttons", []):
                        self.create_button(btn_data["amount"], btn_data["count"])
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        def save_buttons(self):
            data = {
                "buttons": [{"amount": btn["amount"], "count": btn["count"].get()} for btn in self.buttons]
            }
            with open("buttons.json", "w") as file:
                json.dump(data, file)

        def on_closing(self):
            self.running = False
            self.save_buttons()
            self.save_to_db()
            self.conn.close()

        def add_new_button(self):
            amount = simpledialog.askinteger("Input", "Enter water amount (ml):", 
                                           parent=self.parent, minvalue=1)
            if amount:
                self.create_button(amount)

        def add_default_button(self, amount):
            self.create_button(amount)

        def create_button(self, amount, count=0):
            frame = tk.Frame(self.parent)
            frame.pack(pady=5)

            count_var = tk.IntVar(value=count)
            button = tk.Button(frame, text=f"{count_var.get()}", 
                             command=lambda: self.increment_count(button, count_var, amount))
            button.pack(side=tk.LEFT)

            tk.Label(frame, text=f"{amount} ml").pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(frame, text="x", 
                                    command=lambda: self.delete_button(frame, count_var, amount))
            delete_button.pack(side=tk.LEFT, padx=5)

            self.buttons.append({"frame": frame, "button": button, "count": count_var, "amount": amount})

        def increment_count(self, button, count, amount):
            count.set(count.get() + 1)
            button.config(text=f"{count.get()}")
            self.sum_total += amount
            self.total_label.config(text=f"Total Intake: {self.sum_total} ml")

        def subtract_amount(self):
            amount = simpledialog.askinteger("Input", "Enter water amount to subtract (ml):", 
                                           parent=self.parent, minvalue=1)
            if amount:
                self.sum_total = max(0, self.sum_total - amount)
                self.total_label.config(text=f"Total Intake: {self.sum_total} ml")
                
        def correct_amount(self):
            amount = simpledialog.askinteger("Input", "Correct the amount (ml):", 
                                           parent=self.parent, minvalue=1)
            if amount:
                self.sum_total = max(0, amount)
                self.total_label.config(text=f"Total Intake: {self.sum_total} ml")

        def delete_button(self, frame, count, amount):
            self.buttons = [b for b in self.buttons if b["frame"] != frame]
            frame.destroy()
        
        def cleanup(self):
            pass
    
    _app_instance = WaterIntakeApp(parent)
    
    
def cleanup():
    """Module-level cleanup function called by main.py."""
    global _app_instance
    if _app_instance is not None:
        _app_instance.on_closing()
        _app_instance.cleanup()
        _app_instance = None