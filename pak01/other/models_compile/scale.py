import os
from shutil import copy2
import math

def find_smd_file():
    files = os.listdir()
    smd_files = [f for f in files if f.endswith('.smd') and not f.endswith('.smd.bkp')]
    if smd_files:
        return smd_files[0]
    return None

def rotate_point(x, y, z, rotation_x_radians):
    # Rotate around X axis
    new_y = y * math.cos(rotation_x_radians) - z * math.sin(rotation_x_radians)
    new_z = y * math.sin(rotation_x_radians) + z * math.cos(rotation_x_radians)
    return x, new_y, new_z

def modify_smd(input_file, output_file, scale_factor, height_factor, rotation_x_degrees=0):
    with open(input_file, 'r') as f:
        lines = f.readlines()
   
    in_triangles = False
    in_skeleton = False
    new_lines = []
   
    rotation_x_radians = math.radians(rotation_x_degrees)
   
    for line in lines:
        if line.strip() in ['version 1', 'nodes', '0 "root" -1', 'end', 'skeleton', 'time 0', 'triangles']:
            new_lines.append(line)
            if line.strip() == 'skeleton':
                in_skeleton = True
            elif line.strip() == 'triangles':
                in_skeleton = False
                in_triangles = True
            continue
           
        if in_skeleton and line.strip().startswith('0 '):
            parts = line.split()
            original_rot_x = float(parts[4])
            new_rot_x = original_rot_x + rotation_x_radians
            
            # First scale
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            
            # Then rotate
            x, y, z = rotate_point(x, y, z, rotation_x_radians)
            
            # Finally add height
            z += height_factor
            
            new_line = f"    0 {x:.6f} {y:.6f} {z:.6f} {new_rot_x:.6f} {parts[5]} {parts[6]}\n"
            new_lines.append(new_line)
            continue
           
        if in_triangles and line.startswith('service_medal'):
            new_lines.append(line)
            continue
           
        if in_triangles and line.strip() and not line.strip() == 'end':
            parts = line.split()
            if len(parts) >= 9:
                # First scale
                orig_x = float(parts[1]) * scale_factor
                orig_y = float(parts[2]) * scale_factor
                orig_z = float(parts[3]) * scale_factor
                
                # Then rotate
                new_x, new_y, new_z = rotate_point(orig_x, orig_y, orig_z, rotation_x_radians)
                
                # Finally add height
                new_z += height_factor
                
                # Get normal vector components
                normal_x = float(parts[4])
                normal_y = float(parts[5])
                normal_z = float(parts[6])
                
                # Rotate the normal vector too
                new_normal_x, new_normal_y, new_normal_z = rotate_point(normal_x, normal_y, normal_z, rotation_x_radians)
                
                # Get the original bone index from parts[0]
                bone_index = parts[0]
                scaled_line = f"  {bone_index} {new_x:.6f} {new_y:.6f} {new_z:.6f} {new_normal_x:.6f} {new_normal_y:.6f} {new_normal_z:.6f} {parts[7]} {parts[8]}"
                if len(parts) > 9:
                    scaled_line += " " + " ".join(parts[9:])
                scaled_line += "\n"
                
                new_lines.append(scaled_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
   
    with open(output_file, 'w') as f:
        f.writelines(new_lines)

def main():
    smd_file = find_smd_file()
    if not smd_file:
        print("No .smd file found in current directory!")
        return
   
    backup_file = f"{smd_file}.bkp"
    source_file = backup_file if os.path.exists(backup_file) else smd_file
    
    if not os.path.exists(backup_file):
        copy2(smd_file, backup_file)
        print(f"Created backup: {backup_file}")
    else:
        print(f"Using existing backup as source: {backup_file}")
   
    temp_file = "temp_scaled.smd"
   
    scale_factor = 1  # Scale
    height_factor = 3  # Height adjustment (positive moves up)
    rotation_x_degrees = 0  # Rotation in degrees (positive tilts backward)
   
    modify_smd(source_file, temp_file, scale_factor, height_factor, rotation_x_degrees)
   
    os.replace(temp_file, smd_file)
    print(f"Modified {smd_file} successfully!")

if __name__ == "__main__":
    main()