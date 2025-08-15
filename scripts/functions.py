import os
import imagehash
import sys
import re
import logging

from PIL import Image
logger = logging.getLogger(__name__)

def get_image_hashes(var, hash_size=8, hash_method='dhash'):
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
    logger.info(f"Scanning directory: {var.target_directory}")
    
    # Reset the global dictionary for each new scan

    for dirpath, _, filenames in os.walk(var.target_directory):
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
                        logger.error(f"Error: Unsupported hash method '{hash_method}'. Using phash instead.")
                        image_hash = imagehash.phash(img, hash_size=hash_size)

                    # Store the hash and file path. The hash is converted to a string
                    # to be used as a dictionary key.
                    hash_str = str(image_hash)
                    if hash_str in var.image_hashes:
                        var.image_hashes[hash_str].append(file_path)
                    else:
                        var.image_hashes[hash_str] = [file_path]
            
            except Exception as e:
                # Catch any errors during image processing or file access
                logger.error(f"Could not process file {file_path}: {e}")
                continue
    
    logger.info("Scanning complete.")
    return var.image_hashes

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
                        logger.error(f"Error comparing hashes: {e}")
                        continue

        if len(current_group) > 1:
            duplicates.append(current_group)
    
    return duplicates

def delete_duplicates(var, deletion_strategy='keep_first'):
    def numeric_key(path):
        filename = os.path.splitext(os.path.basename(path))[0]
        numbers = re.findall(r'\d+', filename)
        numeric_tuple = tuple(int(num) for num in numbers) if numbers else (float('inf'),)
        return (numeric_tuple, len(filename), filename.lower())

    def original_file_key(path):
        # A specific key to prioritize the original file for deletion logic
        filename = os.path.basename(path)
        return 'copy' in filename.lower()

    """
    Deletes duplicate images from the disk based on a chosen strategy.
    
    Args:
        duplicate_groups (list): A list of duplicate groups.
        deletion_strategy (str): 'keep_first' is the default.
    """
    if not var.duplicate_groups:
        logger.info("No duplicate images to delete.")
        return

    # Sort the duplicate_groups list for a cleaner display
    var.duplicate_groups.sort(key=lambda group: numeric_key(group[0]))

    logger.info(f"\nFound {len(var.duplicate_groups)} duplicate groups.")
    
    files_to_delete = []
    
    # Determine which files to delete based on the strategy
    for group in var.duplicate_groups:
        # Sort the inner group using a clear deletion key
        group.sort(key=original_file_key)

        if deletion_strategy == 'keep_first':
            # The first item is now guaranteed to be the 'original'
            files_to_delete.extend(group[1:])
        elif deletion_strategy == 'keep_smallest':
            # This logic remains the same, but the inner group is still sorted by the new key
            files_and_sizes = [(path, os.path.getsize(path)) for path in group]
            files_and_sizes.sort(key=lambda x: x[1])
            files_to_delete.extend([path for path, _ in files_and_sizes[1:]])
        else:
            logger.info(f"Error: Unsupported deletion strategy '{deletion_strategy}'. Using 'keep_first'.")
            files_to_delete.extend(group[1:])

    # Print a summary of files to be deleted (Dry Run)
    logger.info("\n--- Dry Run: Duplicate files ---")
    for group in var.duplicate_groups:
        # The inner group is already sorted for deletion, so we can just print it
        logger.info(f"{group[0]}: {group[1:]}")
    logger.info("-----------------------------------")
    
    # Prompt user for confirmation before deletion
    response = input(f"\nAre you sure you want to delete {len(files_to_delete)} files? (yes/no): ").lower()
    
    if response in ['yes', 'y']:
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                #os.remove(file_path)
                deleted_count += 1
                logger.info(f"Deleted: {file_path}")
            except OSError as e:
                logger.error(f"Error deleting {file_path}: {e}")
        
        logger.info(f"\nSuccessfully deleted {deleted_count} files.")
    else:
        logger.info("Deletion cancelled by user.")

if __name__=="__main__":
    
    image_hashes=get_image_hashes(r"D:\Pictures\Bears")
    #print(f"image_hashes:{image_hashes}")
    
    duplicates_=find_duplicates(image_hashes)
    #print(duplicates_)
    result=delete_duplicates(duplicates_)