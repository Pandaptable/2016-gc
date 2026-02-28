import os
import subprocess
import hashlib

def split_file(file_path, chunk_size_mb=485):
    # Convert chunk size to bytes
    chunk_size = chunk_size_mb * 1024 * 1024
   
    # Create output directory
    base_name = os.path.splitext(file_path)[0]
    output_dir = f"{base_name}_chunks"
    os.makedirs(output_dir, exist_ok=True)
   
    # Read and split the file
    with open(file_path, 'rb') as f:
        chunk_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
           
            output_path = os.path.join(output_dir, f"{os.path.basename(file_path)}.{chunk_num:03d}")
            
            # Calculate MD5 hash
            chunk_hash = hashlib.md5(chunk).hexdigest()
            
            # Write chunk to file
            with open(output_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
            
            # Print chunk filename and its hash
            print(f"Chunk: {os.path.basename(output_path)}")
            print(f"MD5:   {chunk_hash}")
            print("-" * 70)
            
            chunk_num += 1
   
    print(f"\nSplit complete! Created {chunk_num-1} chunks in '{output_dir}'")

if __name__ == "__main__":
    file_path = input("Enter the path to your .7z archive: ")
    split_file(file_path)