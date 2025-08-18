import tkinter as tk
from tkinter import filedialog
import traceback

from scripts.variables import Variables
from scripts.logger import loggerSetup

import logging
import sys

# Step 1: Create a custom handler to redirect logs to the Text widget
class TkinterTextHandler(logging.Handler):
    """
    A custom logging handler that redirects log messages to a Tkinter Text widget.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state=tk.DISABLED) # Make the widget read-only
        self.setFormatter(logging.Formatter('%(message)s'))


    def emit(self, record):
        # Format the log message
        msg = self.format(record)
        
        # Enable the widget to insert text, then disable it again
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state=tk.DISABLED)
        
        # Scroll to the bottom to show the newest log message
        self.text_widget.see(tk.END)


class MyTinkerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Duplication Detector")
        self.root.geometry("600x700")
        self.root.resizable(False, True)

        # Create a frame to hold all the input widgets
        input_frame = tk.Frame(root)
        input_frame.pack(pady=20)
    
        # Directory Input
        self.label_dir = tk.Label(input_frame, text="Browse or Enter directory.")
        self.label_dir.grid(row=0, column=0, columnspan=2, pady=5)
        
        self.directory_entry = tk.Entry(input_frame, width=50)
        self.directory_entry.grid(row=1, column=0, columnspan=2, pady=5)

        self.button_browse = tk.Button(input_frame, text="Browse Directory", command=self.browse_directory)
        self.button_browse.grid(row=2, column=0, columnspan=2, pady=5)

        # Separator for visual clarity
        tk.Frame(input_frame, height=1, bg="gray").grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        # Threshold Input
        self.threshold_label = tk.Label(input_frame, text="Enter Threshold")
        self.threshold_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.threshold_entry = tk.Entry(input_frame, width=17)
        self.threshold_entry.grid(row=4, column=1, padx=5, pady=5)

        # Deletion Strategy Dropdown
        self.strategy_label = tk.Label(input_frame, text="Deletion Strategy")
        self.strategy_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        
        self.strategy_var = tk.StringVar(root)
        self.strategy_options = ['keep_first', 'keep_smallest']
        self.strategy_var.set(self.strategy_options[0])  # Set default value

        self.strategy_menu = tk.OptionMenu(input_frame, self.strategy_var, *self.strategy_options)
        self.strategy_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        
        # Analyze Button
        self.analyze_button = tk.Button(root, text="Analyze and Run", command=self.analyze_and_run)
        self.analyze_button.pack(pady=10)
        
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)
        
        # Step 2: Add a Text widget for displaying logs
        self.log_text = tk.Text(root)
        self.log_text.pack(pady=10)

        # Add a scrollbar to the text widget
        scrollbar = tk.Scrollbar(root, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Step 3: Redirect logging to the new Text widget
        # Get the root logger instance
        root_logger = logging.getLogger()
        
        # Remove the old console handler
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)

        # Add the new Tkinter text handler
        self.logger_handler = TkinterTextHandler(self.log_text)
        root_logger.addHandler(self.logger_handler)


    def browse_directory(self):
        """
        Opens a directory selection dialog and puts the selected path
        into the entry field.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)
            self.status_label.config(text=f"Selected: {directory}")

    def analyze_and_run(self):
        """
        This function acts as the bridge. It gets the user input from the GUI,
        sets up the variables, and then calls the main function from main.py.
        """
        input_directory = self.directory_entry.get()
        threshold_value = self.threshold_entry.get()
        strategy_value = self.strategy_var.get()

        if not input_directory:
            self.status_label.config(text="Please select a directory first!")
            return

        self.status_label.config(text="Analysis started...")
        self.root.update_idletasks()

        try:
            from main import main
            
            var = Variables()
            var.target_directory = input_directory
            var.threshold = int(threshold_value) if threshold_value else 10
            var.strategy = strategy_value

            main(var)
            self.status_label.config(text="Analysis finished successfully.")
        except Exception as e:
            error_message = f"An error occurred: {e}"
            self.status_label.config(text=error_message)
            traceback.print_exc()

def main():
    # Call the existing logger setup from your scripts folder first
    loggerSetup()
    root = tk.Tk()
    app = MyTinkerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
