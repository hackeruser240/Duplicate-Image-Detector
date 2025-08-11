import sys
import argparse
import os
from scripts.functions import get_image_hashes, find_duplicates, delete_duplicates

def main():
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
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)

    # Use the parsed arguments
    target_directory = args.directory
    threshold = args.threshold
    strategy = args.strategy

    # Perform additional checks not handled by argparse
    # Verify that the provided path is a valid directory
    if not os.path.isdir(target_directory):
        print(f"Error: The provided path '{target_directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
    
    # Step 1: Get all image hashes
    try:
        print(f"Scanning '{target_directory}' with threshold {threshold} and strategy '{strategy}'...")
        hashes_map = get_image_hashes(target_directory)
    except Exception as e:
        print(f"An unexpected error occurred during hashing: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Step 2: Find duplicate groups
    try:
        duplicate_groups = find_duplicates(hashes_map, threshold=threshold)
    except Exception as e:
        print(f"An unexpected error occurred while finding duplicates: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Step 3: Delete duplicates after user confirmation
    try:
        delete_duplicates(duplicate_groups, deletion_strategy=strategy)
    except Exception as e:
        print(f"An unexpected error occurred during deletion: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("\nProcess finished.")

if __name__ == "__main__":
    main()
