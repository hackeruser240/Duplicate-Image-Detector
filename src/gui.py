from tkinter import filedialog, messagebox
from cli_backup.variables import Variables
from cli_backup.functions import delete_duplicates
from gui_backup.helper import setup_gui, setup_logging, browse_directory, clear_log

import _cli
import logging
import tkinter as tk
import traceback

class MyTinkerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Duplication Detector")
        self.root.geometry("600x700")
        #self.root.resizable(True, True)
        
        # 1. Initialize variables
        self.var = Variables()
        self.delete_checkbox_var = tk.BooleanVar()
        self.var.threshold = 10

        # 2. Setup the GUI layout and logging using helper functions
        setup_gui(self)
        setup_logging(self)

    def analyze_and_run(self):
        """
        This function orchestrates the analysis and deletion process for the GUI.
        """
        total_files_to_delete = 0
        input_directory = self.directory_entry.get()
        threshold_value = self.threshold_entry.get()
        strategy_value = self.strategy_var.get()
        
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
            
            logger.info("\n***************")
            logger.info("Starting Script")
            logger.info("***************\n")

            duplicate_groups = _cli.find_and_group_duplicates(self.var)
            self.var.duplicate_groups = duplicate_groups

            if not duplicate_groups:
                self.status_label.config(text="No duplicates or an error occurred.")
                return

            total_files_to_delete = sum(len(group) - 1 for group in duplicate_groups)
            
            if total_files_to_delete > 0:
                if self.var.delete_files:
                    logger.info("Deletion checkbox is checked. Proceeding with deletion...")
                    delete_duplicates(self.var, deletion_strategy=self.var.strategy)
                    self.status_label.config(text="Analysis finished. Duplicates deleted.")
                else:
                    self.status_label.config(text=f"Analysis finished. Found {total_files_to_delete} duplicates. Deletion not requested.")
            else:
                self.status_label.config(text="Analysis finished. No duplicates found.")

            logger.info("\n************")
            logger.info("Script Ended")
            logger.info("************")

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

