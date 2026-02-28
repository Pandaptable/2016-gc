import sys
import subprocess
import pkg_resources

def install_required_packages():
    required = {'pathlib'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print("Installing required packages...")
        python = sys.executable
        for package in missing:
            try:
                subprocess.check_call([python, '-m', 'pip', 'install', package], 
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
                print(f"Successfully installed {package}")
            except Exception as e:
                print(f"Failed to install {package}: {e}")
                sys.exit(1)
        print("All required packages installed successfully!")

# Install required packages before importing them
install_required_packages()

import os
import hashlib
import datetime
import shutil
import subprocess
import argparse
from pathlib import Path

class AssetProcessor:
    def check_and_create_move_dir(self, move_dir):
        if move_dir:
            move_path = Path(move_dir)
            try:
                move_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory {move_dir}: {e}")
                sys.exit(1)

    def check_and_move_existing_vpks(self, move_dir):
        move_path = Path(move_dir)
        if not move_path.exists():
            return
            
        # Get VPK files that start with input_folder
        vpk_files = move_path.glob(f'{self.input_folder}_*.vpk')
        current_dir = Path('.')
        
        for vpk_file in vpk_files:
            try:
                shutil.move(str(vpk_file), str(current_dir / vpk_file.name))
                print(f"Moved existing {vpk_file.name} from {move_dir} to current directory")
            except Exception as e:
                print(f"Error moving {vpk_file.name}: {e}")

    def kv_to_current(self, move_dir):
        move_path = Path(move_dir)
        bak_file = move_path / f"{self.input_folder}.kv.txt.bak"
        if bak_file.exists():
            try:
                shutil.move(str(bak_file), f"{self.input_folder}.kv.txt.bak")
                print(f"Moved {bak_file.name} from {move_dir} to current directory")
            except Exception as e:
                print(f"Error moving {bak_file.name}: {e}")

    def kv_to_move_dir(self, move_dir):
        bak_file = Path(f"{self.input_folder}.kv.txt.bak")
        if bak_file.exists():
            move_path = Path(move_dir)
            try:
                shutil.move(str(bak_file), str(move_path / bak_file.name))
                print(f"Moved {bak_file.name} back to {move_dir}")
            except Exception as e:
                print(f"Error moving {bak_file.name}: {e}")


    
    def __init__(self, input_folder, vpk_exe_path, chunk_size="100", move_dir=None, move_files=0):
        self.input_folder = input_folder
        self.vpk_exe = Path(vpk_exe_path)
        self.kv_file = f"{input_folder}.kv.txt"
        self.chunk_size = chunk_size
        self.move_dir = move_dir
        self.move_files = move_files
        self.folder_extensions = {
            'materials': ['.vmt', '.vtf'],
            'models': ['.mdl', '.phy', '.ani', '.vtx', '.vvd'],
            'sound': ['.wav', '.mp3', '.txt'],
            'particles': ['.pcf', '.txt'],
            'scripts': ['.res', '.txt'],
            'resource': ['.res', '.txt', '.png'],
            'classes': ['.res'],
            'shaders': ['.vcs']
        }

    def calculate_md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def create_kv_file(self):
        # Delete previous kv file if it exists before writing
        if os.path.exists(self.kv_file):
            os.remove(self.kv_file)

        timestamp = datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S.%f")[:-4]
        
        with open(self.kv_file, 'w') as f:
            f.write(f"//\n")
            f.write(f"//        Keyvalues Control File = \"{self.kv_file}\"\n")
            f.write(f"//        made = {timestamp}\n")
            f.write(f"//\n\n")

    def process_folders(self):
        n = 0
        for folder, extensions in self.folder_extensions.items():
            folder_path = Path(self.input_folder) / folder
            if not folder_path.exists():
                continue

            print(f"Processing {folder}...", end='', flush=True)
            
            # Get all files in the folder and its subfolders
            all_files = []
            for ext in extensions:
                all_files.extend(list(folder_path.rglob(f"*{ext}")))
            
            # Sort files to ensure consistent ordering
            all_files.sort()

            for file_path in all_files:
                rel_path = str(file_path.relative_to(self.input_folder))
                
                with open(self.kv_file, 'a') as f:
                    f.write(f'"{str(file_path)}"\n')
                    f.write("{\n")
                    f.write(f'    "destpath"    "{rel_path}"\n')
                    
                    # Calculate MD5
                    md5_hash = self.calculate_md5(file_path)
                    f.write(f'    "MD5"         "{md5_hash}"\n')
                    f.write("}\n")

                n += 1
                if n >= 100:
                    print(".", end='', flush=True)
                    n = 0
            
            print()  # New line after each folder

    def handle_vpk(self):
        if not self.vpk_exe.exists():
            print("ERROR: VPK executable not found!")
            return False

        print(f"Found VPK tool: {self.vpk_exe}")
        print("VPK tool in action!!!")

        # Check for key files
        if Path("my.privatekey.vdf").exists() and Path("my.publickey.vdf").exists():
            subprocess.run([
                str(self.vpk_exe),
                "-P", "-c", self.chunk_size,
                "-K", "my.privatekey.vdf",
                "-k", "my.publickey.vdf",
                "k",
                self.input_folder,
                self.kv_file
            ])
        else:
            subprocess.run([
                str(self.vpk_exe),
                "-P", "-c", self.chunk_size,
                "k",
                self.input_folder,
                self.kv_file
            ])

        self.backup_kv_file()
        return True

    def backup_kv_file(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Determine backup directory based on move_files setting
        if self.move_files == 1 and self.move_dir:
            backup_dir = Path(self.move_dir) / "oldkvfiles"
        else:
            backup_dir = Path("oldkvfiles")
        
        # Create oldkvfiles directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Current .kv file and its backup
        kv_file = Path(self.kv_file)
        kv_backup = Path(f"{self.kv_file}.bak")
        
        # If there's an existing .bak file, move it to oldkvfiles
        if kv_backup.exists():
            new_backup_name = backup_dir / f"{timestamp}_{kv_backup.name}"
            shutil.move(str(kv_backup), str(new_backup_name))
        
        # If there's a current .kv file, rename it to .bak
        if kv_file.exists():
            shutil.move(str(kv_file), str(kv_backup))
            
        # Clean up the current .kv file if it still exists
        try:
            kv_file.unlink(missing_ok=True)
        except:
            pass
    
    def move_vpk_files(self, move_dir):
        move_path = Path(move_dir)
        
        # Create the destination directory if it doesn't exist
        move_path.mkdir(parents=True, exist_ok=True)
        
        # Get all .vpk files in the current directory
        vpk_files = Path('.').glob('*.vpk')
        
        for vpk_file in vpk_files:
            try:
                shutil.move(str(vpk_file), str(move_path / vpk_file.name))
                print(f"Moved {vpk_file.name} to {move_dir}")
            except Exception as e:
                print(f"Error moving {vpk_file.name}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Asset Processing Script')
    
    parser.add_argument('--vpk_exe', type=str, required=True,
                        help='Path to the VPK executable')
    
    parser.add_argument('--input_folder', type=str, default="pak01",
                        help='Input folder name (default: pak01)')
    
    parser.add_argument('--chunk_size', type=str, default="100",
                        help='Chunk size (default: 100)')
    
    parser.add_argument('--compression', type=int, default=0,
                        help='Enable compression (0=off, 1=on, default: 0)')
    
    parser.add_argument('--compression_split', type=int, default=1, choices=[0, 1],
                    help='Enable split archives for compression (0=off, 1=on, default: 1)')
    
    parser.add_argument('--move_files', type=int, default=0,
                        help='Enable file moving (0=off, 1=on, default: 0)')
    
    parser.add_argument('--move_dir', type=str,
                        help='Directory to move files to (required if move_files=1)')

    args = parser.parse_args()

    # Check if move_dir is provided when move_files is enabled
    if args.move_files == 1 and not args.move_dir:
        parser.error("--move_dir is required when --move_files is set to 1!")

    processor = AssetProcessor(
        args.input_folder, 
        args.vpk_exe, 
        args.chunk_size,
        args.move_dir,
        args.move_files
    )
    
    # Create move_dir if it's provided
    if args.move_dir:
        processor.check_and_create_move_dir(args.move_dir)
    
    # Check and move existing VPK files at start
    print(f"\nChecking for existing VPK files in {args.move_dir}...")
    processor.check_and_move_existing_vpks(args.move_dir)
    
    # Move .bak file to current directory
    print(f"\nChecking for existing .bak file in {args.move_dir}...")
    processor.kv_to_current(args.move_dir)
    
    print(f"\nCreating Keyvalues File {processor.kv_file}...")
    print("Collecting MD5 checksums of files...\n")
    
    print("Please wait... This entire process could take around 2-10 minutes.\n")

    processor.create_kv_file()
    processor.process_folders()
    processor.handle_vpk()
    
    print("\nAll done!")

    # Run compression if compression is 1
    if args.compression == 1:
        try:
            print("\nRunning compression script...")
            input_dir = os.getcwd()  # Current directory where VPK files are
            subprocess.run(["python", "vpk_compress.py", input_dir, "../pak01_compiled", 
                        "--compress-split", str(args.compress_split)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running compression script: {e}")
        except FileNotFoundError:
            print("Error: vpk_compress.py not found in the current directory!")

    # Move VPK files and .bak file if move_files is 1
    if args.move_files == 1:
        print(f"\nMoving VPK files to {args.move_dir}...")
        processor.move_vpk_files(args.move_dir)
        print(f"\nMoving .bak file to {args.move_dir}...")
        processor.kv_to_move_dir(args.move_dir)

if __name__ == "__main__":
    main()