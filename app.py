# Import the Tkinter module
import tkinter as tk
# Import the filedialog and messagebox modules
from tkinter import filedialog, messagebox
# Import the traceback module for detailed error handling
import traceback

# Import other necessary project modules
from scripts.variables import Variables
# We no longer need to import loggerSetup as we handle logging here
# from scripts.logger import loggerSetup 
# Import the new function from main.py for finding duplicates
from main import find_and_group_duplicates
# Import the delete_duplicates function directly
from scripts.functions import delete_duplicates

import logging
import os

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
        self.root.resizable(True, True)
        
        # Initialize the Variables object here to make it accessible
        self.var = Variables()
        # Initialize a Tkinter BooleanVar and link it to the variable class
        self.delete_checkbox_var = tk.BooleanVar()

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
        self.strategy_var.set(self.strategy_options[0])

        self.strategy_menu = tk.OptionMenu(input_frame, self.strategy_var, *self.strategy_options)
        self.strategy_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        
        # New Checkbutton for deletion, linked to the BooleanVar
        self.delete_check = tk.Checkbutton(input_frame, text="Delete duplicates automatically", variable=self.delete_checkbox_var)
        self.delete_check.grid(row=6, column=0, columnspan=2, pady=10)

        # Analyze Button
        self.analyze_button = tk.Button(root, text="Analyze and Run", command=self.analyze_and_run)
        self.analyze_button.pack(pady=10)
        
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)
        
        # Step 2: Add a Text widget for displaying logs
        self.log_text = tk.Text(root, width=70)
        self.log_text.pack(pady=10)

        # Add a scrollbar to the text widget
        scrollbar = tk.Scrollbar(root, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Step 3: Configure the root logger directly inside the app
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Clear any existing handlers to prevent duplicate messages
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Add the FileHandler to write to log.txt
        if not os.path.exists("logs"):
            os.mkdir("logs")
        log_file = os.path.join("logs", 'log.txt')
        file_handler = logging.FileHandler(log_file, "w")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        # Add the custom TkinterTextHandler for the GUI
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
        This function orchestrates the analysis and deletion process for the GUI.
        """
        input_directory = self.directory_entry.get()
        threshold_value = self.threshold_entry.get()
        strategy_value = self.strategy_var.get()
        
        # Get the state of the checkbox and update the variable
        self.var.delete_files = self.delete_checkbox_var.get()
        
        if not input_directory:
            self.status_label.config(text="Please select a directory first!")
            return

        self.status_label.config(text="Analysis started...")
        self.root.update_idletasks()
        
        logger = logging.getLogger(__name__)

        try:
            self.var.target_directory = input_directory
            self.var.threshold = int(threshold_value) if threshold_value else 10
            self.var.strategy = strategy_value
            
            # Step 1: Find the duplicates using the new function
            duplicate_groups = find_and_group_duplicates(self.var)

            if not duplicate_groups:
                self.status_label.config(text="No duplicates or an error occurred.")
                return

            # Count the number of files to be deleted
            total_files_to_delete = sum(len(group) - 1 for group in duplicate_groups)
            
            if total_files_to_delete > 0:
                if self.var.delete_files:
                    # If the checkbox is checked, proceed with deletion
                    logger.info("Deletion checkbox is checked. Proceeding with deletion...")
                    delete_duplicates(self.var, deletion_strategy=self.var.strategy)
                    self.status_label.config(text="Analysis finished. Duplicates deleted.")
                else:
                    # If the checkbox is not checked, just report the findings
                    self.status_label.config(text=f"Analysis finished. Found {total_files_to_delete} duplicates. Deletion not requested.")
            else:
                self.status_label.config(text="Analysis finished. No duplicates found.")

        except Exception as e:
            error_message = f"An error occurred: {e}"
            self.status_label.config(text=error_message)
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = MyTinkerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
