import os
import imagehash
import sys
import re
import logging
from collections import defaultdict
from PIL import Image

logger = logging.getLogger(__name__)

def get_image_hashes(var, hash_size=8, hash_method='dhash'):
    """
    Recursively walks through a directory, computes a perceptual hash for each
    image file, and stores it in a dictionary.
    
    Args:
        var (Variables): The variables object containing the target directory.
        hash_size (int): The size of the hash, which can affect precision.
        hash_method (str): The hashing algorithm to use ('phash', 'ahash', 'dhash').
    
    Returns:
        dict: A dictionary where keys are image hashes and values are a list of
              file paths that share that hash.
    """
    logger.info(f"Scanning directory: {var.target_directory}")
    
    # Use a local dictionary to store hashes for this run.
    image_hashes = defaultdict(list)

    for dirpath, _, filenames in os.walk(var.target_directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Check if the file is an image based on its extension
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                continue

            try:
                # Open the image file
                img = Image.open(file_path)
                
                # Convert to a common format (RGB) to handle different image types
                img = img.convert('RGB')
                
                # Compute the hash based on the selected method
                if hash_method == 'phash':
                    image_hash = str(imagehash.phash(img, hash_size=hash_size))
                elif hash_method == 'ahash':
                    image_hash = str(imagehash.average_hash(img, hash_size=hash_size))
                elif hash_method == 'dhash':
                    image_hash = str(imagehash.dhash(img, hash_size=hash_size))
                else:
                    logger.error(f"Unsupported hash method: {hash_method}")
                    continue

                # Add the hash and file path to the dictionary
                image_hashes[image_hash].append(file_path)
                
            except Exception as e:
                logger.error(f"Could not process file {file_path}: {e}")
                continue

    return image_hashes


def find_duplicates(hashes_map, threshold=10):
    """
    Finds groups of duplicate and near-duplicate images based on a hash map.
    This function is now designed to be stateless and returns a new list.

    Args:
        hashes_map (dict): The dictionary of image hashes and file paths.
        threshold (int): The maximum Hamming distance for near-duplicates.

    Returns:
        list: A list of lists, where each inner list contains the file paths
              of duplicate or near-duplicate images.
    """
    # CRITICAL FIX: We initialize a new, empty list here.
    # This prevents the list from growing with subsequent runs.
    duplicate_groups = []
    
    # Process the hashes for exact duplicates first
    processed_hashes = set()
    for img_hash, file_paths in hashes_map.items():
        if len(file_paths) > 1:
            duplicate_groups.append(file_paths)
            processed_hashes.add(img_hash)

    # Now, find near-duplicates
    all_hashes = list(hashes_map.keys())
    for i in range(len(all_hashes)):
        hash1 = imagehash.hex_to_hash(all_hashes[i])
        
        # If this hash has already been processed as an exact duplicate, skip it
        if all_hashes[i] in processed_hashes:
            continue
            
        group = hashes_map[all_hashes[i]]
        processed_hashes.add(all_hashes[i])
        
        for j in range(i + 1, len(all_hashes)):
            hash2 = imagehash.hex_to_hash(all_hashes[j])
            
            # If this hash has already been processed, skip it
            if all_hashes[j] in processed_hashes:
                continue
                
            hamming_distance = hash1 - hash2
            
            if hamming_distance <= threshold:
                group.extend(hashes_map[all_hashes[j]])
                processed_hashes.add(all_hashes[j])
        
        if len(group) > 1:
            duplicate_groups.append(group)
            
    return duplicate_groups


def delete_duplicates(var, deletion_strategy='keep_first'):
    """
    Deletes duplicate images based on the specified strategy.
    
    Args:
        var (Variables): The variables object containing duplicate groups.
        deletion_strategy (str): The strategy to use for deletion.
                                 'keep_first' or 'keep_smallest'.
    """
    logger.info("Starting deletion process...")
    files_to_delete = []

    # This is the corrected and restored logic to ensure the "original" file is kept.
    for group in var.duplicate_groups:
        if deletion_strategy == 'keep_first':
            # We sort the group to ensure that the original file (without " - Copy")
            # is always at the beginning of the list, so it will be kept.
            def original_file_key(file_path):
                # A simple check to see if the filename contains " - Copy"
                # Files without the string will have a lower (0) value and be sorted first.
                return " - Copy" in os.path.basename(file_path)

            group.sort(key=original_file_key)
            files_to_delete.extend(group[1:])
        elif deletion_strategy == 'keep_smallest':
            # Sort by file size (smallest first) and delete all but the smallest
            files_and_sizes = [(f, os.path.getsize(f)) for f in group]
            files_and_sizes.sort(key=lambda x: x[1])
            files_to_delete.extend([f for f, s in files_and_sizes[1:]])
        else:
            logger.info(f"Error: Unsupported deletion strategy '{deletion_strategy}'. Using 'keep_first'.")
            files_to_delete.extend(group[1:])

    # Print a summary of files to be deleted (Dry Run)
    logger.info("\n--- Duplicate files ---")
    for group in var.duplicate_groups:
        logger.info(f"Group with original kept file:")
        logger.info(f"  - Kept: {group[0]}")
        logger.info(f"  - Deleting:")
        for file_path in group[1:]:
            logger.info(f"    - {file_path}")
    logger.info("-----------------------------------\n")
    
    deleted_count = 0
    if not var.dry_run:
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                deleted_count += 1
            except OSError as e:
                logger.error(f"Error deleting {file_path}: {e}")
    else:
        # This is the dry run block
        logger.info("Dry run enabled. No files will be deleted.")
        for file_path in files_to_delete:
            logger.info(f"Would have deleted: {file_path}")
    
    if not var.dry_run:
        logger.info(f"\nSuccessfully deleted {deleted_count} files.")
    else:
        logger.info(f"\nNo files were deleted because dry run was enabled.")