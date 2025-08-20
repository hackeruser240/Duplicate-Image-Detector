import sys
import argparse
import os
import logging
from cli_backup.functions import get_image_hashes, find_duplicates, delete_duplicates
from cli_backup.variables import Variables
from cli_backup.logger import loggerSetup

def find_and_group_duplicates(var):
    """
    Finds and groups duplicate images without prompting for deletion.
    This function is designed to be called by the GUI.
    """
    logger = logging.getLogger(__name__)

    # Verify that the provided path is a valid directory
    if not os.path.isdir(var.target_directory):
        logger.error(f"Error: The provided path '{var.target_directory}' is not a valid directory.")
        return []

    # Step 1: Get all image hashes
    try:
        logger.info(f"Scanning '{var.target_directory}' with threshold {var.threshold} and strategy '{var.strategy}'...")
        hashes_map = get_image_hashes(var)
    except Exception as e:
        logger.error(f"An unexpected error occurred during hashing: {e}")
        return []

    # Step 2: Find duplicate groups using the corrected function
    try:
        duplicate_groups = find_duplicates(hashes_map, threshold=var.threshold)
        logger.info(f"Successfully found {len(duplicate_groups)} groups of duplicates.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while finding duplicates: {e}")
        return []

    return duplicate_groups

def main(var):
    """
    The main function to run the duplicate image detection and deletion tool.
    This is for command-line execution and is not used by the GUI.
    """
    logger.info("\n***************")
    logger.info("Starting Script")
    logger.info("***************\n")
    
    if not os.path.isdir(var.target_directory):
        logger.error(f"Error: The provided path '{var.target_directory}' is not a valid directory.")
        sys.exit(1)

    try:
        logger.info(f"Scanning '{var.target_directory}' with threshold {var.threshold} and strategy '{var.strategy}'...")
        hashes_map = get_image_hashes(var)
    except Exception as e:
        logger.info(f"An unexpected error occurred during hashing: {e}")
        sys.exit(1)
    
    try:
        var.duplicate_groups = find_duplicates(hashes_map, threshold=var.threshold)
        logger.info(f"Successfully found duplicate groups")
    except Exception as e:
        logger.error(f"An unexpected error occurred while finding duplicates: {e}")
        sys.exit(1)

    try:
        delete_duplicates(var, deletion_strategy=var.strategy)
    except Exception as e:
        logger.error(f"An unexpected error occurred during deletion: {e}")
        sys.exit(1)
        
    logger.info("\n************")
    logger.info("Script Ended")
    logger.info("************")

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

    logger = loggerSetup()
    logger = logging.getLogger(__name__)

    try:
        args = parser.parse_args()
    except Exception as e:        
        logger.info(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)
        
    
    var = Variables()
    var.target_directory = args.directory
    var.threshold = args.threshold
    var.strategy = args.strategy
    var.delete_files = True if args.delete_files.lower() == 'yes' else False

    main(var)