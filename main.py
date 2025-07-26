import tkinter as tk
from tkinter import ttk
import os
from importlib import import_module

class TabbedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tabbed Python App")
        self.geometry("600x400")

        # Create notebook (tab container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True, fill='both')

        # Create tabs
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab1, text="Blood Sugar")
        self.notebook.add(self.tab2, text="Water Tracker")
        self.notebook.add(self.tab3, text="Weight Tracker")

        # Store script modules for cleanup
        self.script_modules = {}

        # Load and display each script's content
        self.load_script("script1", self.tab1, "tab1")
        self.load_script("script2", self.tab2, "tab2")
        self.load_script("script3", self.tab3, "tab3")

        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_script(self, script_name, tab, tab_id):
        try:
            # Import the module dynamically
            module = import_module(script_name)
            self.script_modules[tab_id] = module
            # Call the create_content function from the script, passing the tab as parent
            module.create_content(tab)
        except Exception as e:
            # Display error in the tab if the script fails
            error_label = tk.Label(tab, text=f"Error loading {script_name}: {str(e)}", fg="red")
            error_label.pack(pady=10)

    def on_closing(self):
        # Call cleanup for each script that has a cleanup method
        for tab_id, module in self.script_modules.items():
            if hasattr(module, 'cleanup'):
                try:
                    module.cleanup()
                except Exception as e:
                    print(f"Error during cleanup of {tab_id}: {e}")
        # Destroy the main window
        self.destroy()

if __name__ == "__main__":
    app = TabbedApp()
    app.mainloop()