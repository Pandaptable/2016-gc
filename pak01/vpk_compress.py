import os
import hashlib
import sys
import subprocess
import shutil
import argparse
import traceback
from concurrent.futures import ThreadPoolExecutor

# Try to import py7zr, install if not present
try:
    import py7zr
except ImportError:
    print("py7zr package not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "py7zr"])
    import py7zr
    print("py7zr installed successfully!")

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def delete_existing_archive(archive_path):
    if os.path.exists(archive_path):
        try:
            os.remove(archive_path)
            print(f"Deleted existing archive: {archive_path}")
        except Exception as e:
            print(f"Error deleting archive {archive_path}: {str(e)}")

def compress_file(input_path, output_path):
    try:
        print(f"Starting compression of {input_path} to {output_path}")
        filters = [{"id": py7zr.FILTER_LZMA2, "preset": 9}]
        
        # Compress with maximum compression
        with py7zr.SevenZipFile(output_path, 'w', filters=filters) as archive:
            print(f"Adding {os.path.basename(input_path)} to archive...")
            archive.write(input_path, os.path.basename(input_path))
        
        # Verify the archive was created
        if os.path.exists(output_path):
            print(f"Successfully created archive: {output_path}")
            print(f"Archive size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        else:
            print(f"Error: Archive file was not created at {output_path}")
            
    except Exception as e:
        print(f"Error compressing {input_path}:")
        print(traceback.format_exc())
        raise

def process_single_vpk(args):
    try:
        filename, directory, dest_dir = args
        vpk_path = os.path.join(directory, filename)
        hash_file_path = os.path.join(dest_dir, filename + ".txt")
        archive_path = os.path.join(dest_dir, filename + ".7z")
        
        print(f"\nProcessing {filename}...")
        print(f"VPK path: {vpk_path}")
        print(f"Archive path: {archive_path}")
        
        current_hash = calculate_md5(vpk_path)
        
        # If hash file doesn't exist, create it
        if not os.path.exists(hash_file_path):
            print(f"Creating hash file for {filename}")
            with open(hash_file_path, "w") as f:
                f.write(current_hash)
            print(f"Starting compression for {filename}...")
            delete_existing_archive(archive_path)
            compress_file(vpk_path, archive_path)
            return
        
        # Read stored hash
        with open(hash_file_path, "r") as f:
            stored_hash = f.read().strip()
        
        # If hash is different or archive doesn't exist
        if current_hash != stored_hash or not os.path.exists(archive_path):
            if current_hash != stored_hash:
                print(f"Hash mismatch detected for {filename}")
            else:
                print(f"No archive found for {filename}")
            print(f"Starting compression for {filename}...")
            
            with open(hash_file_path, "w") as f:
                f.write(current_hash)
            
            delete_existing_archive(archive_path)
            compress_file(vpk_path, archive_path)
            
    except Exception as e:
        print(f"Error processing {filename}:")
        print(traceback.format_exc())

def process_vpk_files(directory, dest_dir):
    create_directory_if_not_exists(dest_dir)
    
    # Get list of VPK files
    vpk_files = [(f, directory, dest_dir) 
                 for f in os.listdir(directory) 
                 if f.endswith(".vpk")]
    
    print(f"Found {len(vpk_files)} VPK files to process")
    
    # Use ThreadPoolExecutor to process files in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:  # Using 4 workers for parallel processing
        executor.map(process_single_vpk, vpk_files)

def main():
    parser = argparse.ArgumentParser(description='Process VPK files and store archives in specified location')
    parser.add_argument('input_dir', help='Directory containing VPK files to process')
    parser.add_argument('dest_dir', help='Destination directory for hash files and archives')
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    dest_dir = os.path.abspath(args.dest_dir)
    
    print("Starting VPK file processing...")
    print(f"Input directory: {input_dir}")
    print(f"Destination directory: {dest_dir}")
    
    create_directory_if_not_exists(dest_dir)
    process_vpk_files(input_dir, dest_dir)
    print("Processing complete!")

if __name__ == "__main__":
    main()