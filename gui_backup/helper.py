# gui/helper.py

import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox

# Get a logger instance. This logger will use the handlers configured in app.py
# The name `__name__` ensures that the logger is unique to this module.
logger = logging.getLogger(__name__)

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
        """
        Emits a log record to the Tkinter Text widget.
        """
        # Format the log message
        msg = self.format(record)
        
        # Enable the widget to insert text, then disable it again
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.config(state=tk.DISABLED)
        
        # Scroll to the bottom to show the newest log message
        self.text_widget.see(tk.END)

def setup_gui(app):
    """
    Configures all the GUI widgets and their layout,
    attaching them to the MyTinkerApp instance.
    """
    input_frame = tk.Frame(app.root)
    input_frame.pack(pady=20)
    
    # Directory Input
    app.label_dir = tk.Label(input_frame, text="Browse or Enter directory.")
    app.label_dir.grid(row=0, column=0, columnspan=2, pady=5)        
    app.directory_entry = tk.Entry(input_frame, width=50)
    app.directory_entry.grid(row=1, column=0, columnspan=2, pady=5)
    app.button_browse = tk.Button(input_frame, text="Browse Directory", command=lambda: browse_directory(app.directory_entry, app.status_label))
    app.button_browse.grid(row=2, column=0, columnspan=2, pady=5)

    # Separator for visual clarity
    #tk.Frame(input_frame, height=1, bg="gray").grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

    # Threshold Input
    app.threshold_label = tk.Label(input_frame, text="Enter Threshold:")
    app.threshold_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
    app.threshold_entry = tk.Entry(input_frame, width=10)
    app.threshold_entry.insert(0, str(app.var.threshold))
    app.threshold_entry.grid(row=4, column=1, padx=5, pady=5)

    # Deletion Strategy Dropdown
    app.strategy_label = tk.Label(input_frame, text="Deletion Strategy:")
    app.strategy_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")        
    app.strategy_var = tk.StringVar(app.root)
    app.strategy_options = ['keep_first', 'keep_smallest']
    app.strategy_var.set(app.strategy_options[0])
    app.strategy_menu = tk.OptionMenu(input_frame, app.strategy_var, *app.strategy_options)
    app.strategy_menu.config(width=1)
    app.strategy_menu.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
    
    # New Checkbutton for deletion, linked to the BooleanVar
    app.delete_check = tk.Checkbutton(input_frame, text="Delete duplicates automatically", variable=app.delete_checkbox_var)
    app.delete_check.grid(row=6, column=0, columnspan=2)

    # Analyze Button
    # Create a frame to hold both buttons
    button_frame = tk.Frame(app.root)
    button_frame.pack(pady=0)

    # Pack the "Analyze and Run" button into the new frame
    app.analyze_button = tk.Button(button_frame, text="Analyze and Run", command=app.analyze_and_run)
    app.analyze_button.pack(side=tk.LEFT, padx=5)

    # Pack the "Clear Log" button next to it
    app.clear_button = tk.Button(button_frame, text="Clear Log", command=lambda: clear_log(app.log_text))
    app.clear_button.pack(side=tk.LEFT, padx=5)
         
    app.status_label = tk.Label(app.root, text="")
    app.status_label.pack(pady=5)

    # --- FRAME FOR LOGS ---
    log_frame = tk.Frame(app.root)
    log_frame.pack(pady=(0, 10), fill=tk.BOTH, expand=True)

    # Add a Text widget for displaying logs inside the log frame
    app.log_text = tk.Text(log_frame)
    app.log_text.grid(row=0, column=0, sticky="nsew")

    # Add a scrollbar to the text widget inside the log frame
    scrollbar = tk.Scrollbar(log_frame, command=app.log_text.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    app.log_text.config(yscrollcommand=scrollbar.set)

    # Configure the log_frame's columns to expand when the window is resized
    log_frame.grid_columnconfigure(0, weight=1)
    log_frame.grid_rowconfigure(0, weight=1)

def setup_logging(app):
    """
    Configures the root logger to handle both file and GUI logging.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%Y %I:%M:%S %p')

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
    app.logger_handler = TkinterTextHandler(app.log_text)
    root_logger.addHandler(app.logger_handler)

def browse_directory(directory_entry, status_label):
    """
    Opens a directory selection dialog and puts the selected path
    into the entry field.
    """
    directory = filedialog.askdirectory()
    if directory:
        normalized_path = os.path.normpath(directory)
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, normalized_path)
        status_label.config(text=f"Selected: {normalized_path}")
        logger.info(f"Directory selected: {normalized_path}")

def clear_log(log_text):
    """
    Clears all text from the log display widget.
    """
    log_text.config(state=tk.NORMAL)
    log_text.delete('1.0', tk.END)
    log_text.config(state=tk.DISABLED)
