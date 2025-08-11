import os
from PIL import Image
import imagehash
import sys
import shutil

# This dictionary stores the hashes and their corresponding file paths.
# It is used to build a comprehensive map of all images in the directory.
image_hashes = {}

def get_image_hashes(directory, hash_size=8, hash_method='dhash'):
    """
    Recursively walks through a directory, computes a perceptual hash for each
    image file, and stores it in the global image_hashes dictionary.
    
    Args:
        directory (str): The path to the directory to scan.
        hash_size (int): The size of the hash, which can affect precision.
                         A larger size (e.g., 16) is more precise but slower.
        hash_method (str): The hashing algorithm to use ('phash', 'ahash', 'dhash').
                           'phash' is recommended for its robustness.
    
    Returns:
        dict: A dictionary where keys are image hashes and values are a list of
              file paths that share that hash.
    """
    print(f"Scanning directory: {directory}")
    
    # Reset the global dictionary for each new scan
    global image_hashes
    image_hashes = {}

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Check if the file is an image based on its extension
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                continue

            try:
                with Image.open(file_path) as img:
                    # Convert to RGB to ensure compatibility with imagehash, as some
                    # images might be in a different mode (e.g., RGBA, L).
                    img = img.convert('RGB')
                    
                    # Compute the hash using the specified method
                    if hash_method == 'phash':
                        image_hash = imagehash.phash(img, hash_size=hash_size)
                    elif hash_method == 'ahash':
                        image_hash = imagehash.average_hash(img, hash_size=hash_size)
                    elif hash_method == 'dhash':
                        image_hash = imagehash.dhash(img, hash_size=hash_size)
                    else:
                        print(f"Error: Unsupported hash method '{hash_method}'. Using phash instead.")
                        image_hash = imagehash.phash(img, hash_size=hash_size)

                    # Store the hash and file path. The hash is converted to a string
                    # to be used as a dictionary key.
                    hash_str = str(image_hash)
                    if hash_str in image_hashes:
                        image_hashes[hash_str].append(file_path)
                    else:
                        image_hashes[hash_str] = [file_path]
            
            except Exception as e:
                # Catch any errors during image processing or file access
                print(f"Could not process file {file_path}: {e}", file=sys.stderr)
                continue
    
    print("Scanning complete.")
    return image_hashes

def find_duplicates(hashes_map, threshold=10):
    """
    Finds groups of exact and near-duplicate images based on their hashes.
    
    Args:
        hashes_map (dict): The dictionary of hashes and file paths returned by
                           get_image_hashes.
        threshold (int): The maximum allowed Hamming distance for two images
                         to be considered near-duplicates. A value of 0 means
                         only exact duplicates are found.
    
    Returns:
        list: A list of lists, where each inner list represents a group of
              duplicate image file paths.
    """
    duplicates = []
    processed_hashes = set()
    
    # Iterate through all hashes to find duplicates
    for hash_str, file_paths in hashes_map.items():
        # Skip hashes that have already been processed as part of another group
        if hash_str in processed_hashes:
            continue
        
        current_group = file_paths[:]
        processed_hashes.add(hash_str)
        
        # Check for near-duplicates if the threshold is greater than 0
        if threshold > 0:
            for other_hash_str, other_file_paths in hashes_map.items():
                if hash_str != other_hash_str and other_hash_str not in processed_hashes:
                    try:
                        # Compute the Hamming distance between two hashes
                        hash1 = imagehash.hex_to_hash(hash_str)
                        hash2 = imagehash.hex_to_hash(other_hash_str)
                        if hash1 - hash2 <= threshold:
                            current_group.extend(other_file_paths)
                            processed_hashes.add(other_hash_str)
                    except Exception as e:
                        print(f"Error comparing hashes: {e}", file=sys.stderr)
                        continue

        if len(current_group) > 1:
            duplicates.append(current_group)
    
    return duplicates

def delete_duplicates(duplicate_groups, deletion_strategy='keep_first'):
    """
    Deletes duplicate images from the disk based on a chosen strategy.
    
    Args:
        duplicate_groups (list): A list of duplicate groups, as returned by
                                 find_duplicates.
        deletion_strategy (str): The strategy to determine which image to keep.
                                 'keep_first' is the default.
    """
    if not duplicate_groups:
        print("No duplicate images to delete.")
        return

    print(f"\nFound {len(duplicate_groups)} duplicate groups.")
    
    files_to_delete = []
    
    # Determine which files to delete based on the strategy
    for group in duplicate_groups:
        if deletion_strategy == 'keep_first':
            # Keep the first image found in the group
            files_to_delete.extend(group[1:])
        elif deletion_strategy == 'keep_smallest':
            # Keep the image with the smallest file size
            files_and_sizes = [(path, os.path.getsize(path)) for path in group]
            files_and_sizes.sort(key=lambda x: x[1])
            files_to_delete.extend([path for path, _ in files_and_sizes[1:]])
        else:
            print(f"Error: Unsupported deletion strategy '{deletion_strategy}'. Using 'keep_first'.")
            files_to_delete.extend(group[1:])
    
    # Print a summary of files to be deleted (Dry Run)
    print("\n--- Dry Run: Files to be deleted ---")
    for file in files_to_delete:
        print(file)
    print("-----------------------------------")
    
    # Prompt user for confirmation before deletion
    response = input(f"\nAre you sure you want to delete {len(files_to_delete)} files? (yes/no): ").lower()
    
    if response == 'yes' or 'y':
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                # Use os.remove to delete the file
                os.remove(file_path)
                deleted_count += 1
                print(f"Deleted: {file_path}")
            except OSError as e:
                print(f"Error deleting {file_path}: {e}", file=sys.stderr)
        
        print(f"\nSuccessfully deleted {deleted_count} files.")
    else:
        print("Deletion cancelled by user.")

if __name__=="__main__":
    image_hashes=get_image_hashes("D:\Pictures\Bears")
    print(f"image_hashes:{list(image_hashes)}")