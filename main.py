import sys
import argparse
import os
import logging
from scripts.functions import get_image_hashes, find_duplicates, delete_duplicates
from scripts.variables import Variables
from scripts.logger import loggerSetup

def main(var):
    """
    The main function to run the duplicate image detection and deletion tool.
    
    This function handles command-line arguments using the argparse module,
    orchestrates the workflow by calling functions from the scripts.functions
    module, and provides a user interface for confirming deletions.
    """   

    # 1. Create a new ArgumentParser object
    parser = argparse.ArgumentParser(
        description="A tool to detect and delete duplicate and near-duplicate images based on their content."
    )
    
    # 2. Add required positional argument for the directory path
    parser.add_argument(
        "directory",
        type=str,
        help="The path to the directory to scan for duplicate images."
    )
    
    # 3. Add optional argument for the near-duplicate threshold
    parser.add_argument(
        "--threshold",
        type=int,
        default=10,
        help="The maximum Hamming distance for two images to be considered near-duplicates. (default: 10)"
    )
    
    # 4. Add optional argument for the deletion strategy with choices
    parser.add_argument(
        "--strategy",
        type=str,
        default='keep_first',
        choices=['keep_first', 'keep_smallest'],
        help="The strategy to use for deletion: 'keep_first' or 'keep_smallest'. (default: 'keep_first')"
    )
    
    # 5. Parse the command-line arguments
    try:
        args = parser.parse_args()
    except Exception as e:
        logger.info(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)

    # Use the parsed arguments
    var.target_directory = args.directory
    var.threshold = args.threshold
    var.strategy = args.strategy

    # Perform additional checks not handled by argparse
    # Verify that the provided path is a valid directory
    if not os.path.isdir(var.target_directory):
        logger.error(f"Error: The provided path '{var.target_directory}' is not a valid directory.")
        sys.exit(1)
    
    # Step 1: Get all image hashes
    try:
        logger.info(f"Scanning '{var.target_directory}' with threshold {var.threshold} and strategy '{var.strategy}'...")
        hashes_map = get_image_hashes(var)
    except Exception as e:
        logger.info(f"An unexpected error occurred during hashing: {e}")
        sys.exit(1)
    
    # Step 2: Find duplicate groups
    try:
        var.duplicate_groups = find_duplicates(hashes_map, threshold=var.threshold)
        logger.info(f"Successfully found duplicate groups")
    except Exception as e:
        logger.error(f"An unexpected error occurred while finding duplicates: {e}")
        sys.exit(1)
    
    # Step 3: Delete duplicates after user confirmation
    try:
        delete_duplicates(var, deletion_strategy=var.strategy)
    except Exception as e:
        logger.error(f"An unexpected error occurred during deletion: {e}")
        sys.exit(1)
        
    logger.info("\nProcess finished.")

if __name__ == "__main__":

    # Configure the root logger once
    loggerSetup()
    
    # Get a logger instance for this module; it will inherit handlers from the root logger
    logger = logging.getLogger(__name__)

    var=Variables()
    main(var)