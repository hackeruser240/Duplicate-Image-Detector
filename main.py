import sys
import argparse
import os
import logging
from scripts.functions import get_image_hashes, find_duplicates, delete_duplicates
from scripts.variables import Variables
from scripts.logger import loggerSetup

def find_and_group_duplicates(var):
    """
    Finds and groups duplicate images without prompting for deletion.
    This function is designed to be called by the GUI.
    """
    logger = logging.getLogger(__name__)

    # Verify that the provided path is a valid directory
    if not os.path.isdir(var.target_directory):
        logger.error(f"Error: The provided path '{var.target_directory}' is not a valid directory.")
        return None

    # Step 1: Get all image hashes
    try:
        logger.info(f"Scanning '{var.target_directory}' with threshold {var.threshold} and strategy '{var.strategy}'...")
        hashes_map = get_image_hashes(var)
    except Exception as e:
        logger.error(f"An unexpected error occurred during hashing: {e}")
        return None

    # Step 2: Find duplicate groups
    try:
        var.duplicate_groups = find_duplicates(hashes_map, threshold=var.threshold)
        logger.info(f"Successfully found {len(var.duplicate_groups)} groups of duplicates.")
        return var.duplicate_groups
    except Exception as e:
        logger.error(f"An unexpected error occurred while finding duplicates: {e}")
        return None

def main(var):
    """
    The main function for the command-line interface.
    This function orchestrates the workflow, including user prompts for deletion.
    """   
    logger = logging.getLogger(__name__)
    
    # Call the function to find duplicates
    duplicate_groups = find_and_group_duplicates(var)
    if duplicate_groups is None:
        sys.exit(1)
        
    # Step 3: Delete duplicates after user confirmation (for CLI)
    total_files_to_delete = sum(len(group) - 1 for group in duplicate_groups)
    if total_files_to_delete > 0:
        confirm = input(f"Are you sure you want to delete {total_files_to_delete} files? (yes/no): ")
        if confirm.lower() == 'yes':
            try:
                delete_duplicates(var, deletion_strategy=var.strategy)
            except Exception as e:
                logger.error(f"An unexpected error occurred during deletion: {e}")
                sys.exit(1)
            logger.info("Deletion complete.")
        else:
            logger.info("Deletion cancelled.")
    else:
        logger.info("No duplicates found to delete.")

    logger.info("\nProcess finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A tool to detect and delete duplicate and near-duplicate images based on their content."
    )
    
    parser.add_argument(
        "directory",
        type=str,
        help="The path to the directory to scan for duplicate images."
    )
    
    parser.add_argument(
        "--threshold",
        type=int,
        default=10,
        help="The maximum Hamming distance for two images to be considered near-duplicates. (default: 10)"
    )
    
    parser.add_argument(
        "--strategy",
        type=str,
        default='keep_first',
        choices=['keep_first', 'keep_smallest'],
        help="The strategy to use for deletion: 'keep_first' or 'keep_smallest'. (default: 'keep_first')"
    )
    
    

    parser.add_argument(
        "--delete_files",
        type=str,
        default='yes',
        help="Do you want to delete the files? Yes or No."
    )

    try:
        args = parser.parse_args()
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.info(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)

    loggerSetup()
    
    var = Variables()
    var.target_directory = args.directory
    var.threshold = args.threshold
    var.strategy = args.strategy
    var.delete_files=args.delete_files

    main(var)