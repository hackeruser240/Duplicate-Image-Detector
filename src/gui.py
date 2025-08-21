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
        self.dry_run = tk.BooleanVar()
        self.show_full_logs=tk.BooleanVar(value=False)
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
        
        self.var.dry_run = self.dry_run.get()
        
        if not input_directory:
            self.status_label.config(text="Please select a directory first!")
            return

        self.status_label.config(text="Analysis started...")
        self.root.update_idletasks()
        
        logger = logging.getLogger(__name__)

        try:
            
            try:
                self.var.threshold = int(threshold_value) if threshold_value else 10
            except ValueError as e:
                logger.error(f"Invalid threshold value. Using default of 10. Error: {e}")
                self.var.threshold = 10
                
            self.var.strategy = strategy_value
            self.var.target_directory = input_directory

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
                if self.var.dry_run == False :
                    logger.info("Dry Run is NOT checked. Proceeding with deletion.")
                    delete_duplicates(self.var, deletion_strategy=self.var.strategy)
                    self.status_label.config(text="Analysis finished. Duplicates deleted.")
                
                elif self.var.dry_run == True and self.show_full_logs.get() == True:
                    
                    logger.info("Dry Run is checked. Showing Full Logs.")
                    delete_duplicates(self.var, deletion_strategy=self.var.strategy)
                    self.status_label.config(text="Analysis finished. Duplicates deleted.")
                
                elif self.var.dry_run == True and self.show_full_logs.get() == False:
                    logger.info("Dry Run is checked & not showing Full logs")
                    self.status_label.config(text=f"Analysis finished. Found {total_files_to_delete} duplicates. Deletion not requested.")

                else:
                    logger.error("Some error in catching the conditions")
            else:
                self.status_label.config(text="Analysis finished. No duplicates found.")

            logger.info("\n************")
            logger.info("Script Ended")
            logger.info("************")

        except Exception as e:
            error_message = f"An error occurred: {e}"
            self.status_label.config(text=error_message)
            logger.error(error_message)
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = MyTinkerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

