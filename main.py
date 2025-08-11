import sys
import os
from scripts.functions import get_image_hashes, find_duplicates, delete_duplicates

def main():
    """
    The main function to run the duplicate image detection and deletion tool.
    
    This function handles command-line arguments, orchestrates the workflow
    by calling functions from the scripts.functions module, and provides
    a user interface for confirming deletions.
    """
    # Check for correct number of command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <directory_path> [--threshold <int>] [--strategy <str>]")
        print("Example: python main.py /path/to/my/images --threshold 10 --strategy keep_smallest")
        print("\nNote: The threshold is the maximum Hamming distance for near-duplicates.")
        print("Supported strategies: 'keep_first' (default) or 'keep_smallest'.")
        sys.exit(1)
    
    target_directory = sys.argv[1]

    # Handle optional arguments for near-duplicate threshold and deletion strategy
    threshold = 10  # Default value
    strategy = 'keep_first' # Default value
    
    try:
        if "--threshold" in sys.argv:
            index = sys.argv.index("--threshold")
            if index + 1 < len(sys.argv):
                threshold = int(sys.argv[index + 1])
                print(f"Using a near-duplicate threshold of: {threshold}")
            else:
                print("Error: --threshold flag requires an integer value.", file=sys.stderr)
                sys.exit(1)

        if "--strategy" in sys.argv:
            index = sys.argv.index("--strategy")
            if index + 1 < len(sys.argv):
                strategy = sys.argv[index + 1].lower()
                if strategy not in ['keep_first', 'keep_smallest']:
                    print(f"Warning: Invalid strategy '{strategy}'. Using 'keep_first' instead.", file=sys.stderr)
                    strategy = 'keep_first'
                print(f"Using deletion strategy: {strategy}")
            else:
                print("Error: --strategy flag requires a value.", file=sys.stderr)
                sys.exit(1)
    except ValueError:
        print("Error: The threshold must be an integer.", file=sys.stderr)
        sys.exit(1)

    # Verify that the provided path is a valid directory
    if not os.path.isdir(target_directory):
        print(f"Error: The provided path '{target_directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
    
    # Step 1: Get all image hashes
    try:
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
