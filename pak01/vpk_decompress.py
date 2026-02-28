import os
import sys
import subprocess
import glob

# Try to import py7zr, install if not present
try:
    import py7zr
except ImportError:
    print("py7zr package not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "py7zr"])
    import py7zr
    print("py7zr installed successfully!")

def is_split_archive(archive_path):
    return os.path.exists(archive_path + '.001')

def decompress_file(archive_path, output_directory):
    # If it's a .7z.001 file, use that directly
    if os.path.exists(archive_path + '.001'):
        seven_zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "7za.exe")
        
        if not os.path.exists(seven_zip_path):
            print("Error: 7za.exe not found in script directory!")
            print("Please make sure 7za.exe is in the same directory as this script")
            sys.exit(1)
        
        # Use the .001 file directly
        cmd = f'"{seven_zip_path}" x "{archive_path}.001" -o"{output_directory}"'
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("Split archive extracted successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting split archive: {str(e)}")
            raise
    else:
        # Regular .7z file
        try:
            with py7zr.SevenZipFile(archive_path, 'r') as archive:
                archive.extractall(output_directory)
        except:
            # Fallback to 7za.exe if py7zr fails
            seven_zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "7za.exe")
            cmd = f'"{seven_zip_path}" x "{archive_path}" -o"{output_directory}"'
            subprocess.run(cmd, shell=True, check=True)

def get_file_number(filename):
    # Special case for dir.vpk
    if 'dir' in filename:
        return float('inf')  # Make it sort last
    try:
        return int(filename.split('_')[1].split('.')[0])
    except:
        return float('inf')  # Any other special cases sort last

def process_7z_files(directory):
    found_files = False
    processed_bases = set()  # Keep track of processed base names
    
    # Get all archive files and sort them
    archive_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".7z.001"):  # Look for split archives first
            base_name = filename[:-4]  # Remove .001
            archive_files.append(base_name)
        elif filename.endswith(".7z"):  # Then look for regular archives
            if not any(filename[:-3] + ".7z.001" in f for f in os.listdir(directory)):  # Skip if we already found it as .001
                archive_files.append(filename)
    
    # Sort files numerically, with dir.vpk last
    archive_files = sorted(set(archive_files), key=get_file_number)
    
    for base_name in archive_files:
        found_files = True
        if base_name in processed_bases:
            continue
            
        processed_bases.add(base_name)
        archive_path = os.path.join(directory, base_name)
        vpk_name = base_name[:-3]  # Remove .7z extension
        vpk_path = os.path.join(directory, vpk_name)
        
        # Skip if VPK already exists
        if os.path.exists(vpk_path):
            print(f"Skipping {base_name} - {vpk_name} already exists")
            continue
        
        is_split = os.path.exists(archive_path + '.001')
        print(f"Found {'split' if is_split else 'single'} archive: {base_name}")
        print(f"Decompressing {base_name}...")
        
        try:
            decompress_file(archive_path, directory)
            if not os.path.exists(vpk_path):
                print(f"Warning: {vpk_name} not found after decompression!")
        except Exception as e:
            print(f"Error processing {base_name}: {str(e)}")
    
    if not found_files:
        print("No .7z or .7z.001 files found in the directory!")

def main():
    current_directory = os.getcwd()
    print("Starting 7z file decompression...")
    process_7z_files(current_directory)
    print("Decompression complete!")

if __name__ == "__main__":
    main()