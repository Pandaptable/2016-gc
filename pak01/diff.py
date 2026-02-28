def compare_files(file1_path, file2_path, output_path):
   encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
   
   for enc in encodings:
       try:
           with open(file1_path, 'r', encoding=enc) as f1, open(file2_path, 'r', encoding=enc) as f2:
               # Read as binary to preserve newlines
               content1 = f1.read()
               content2 = f2.read()
               
               lines1 = content1.splitlines(keepends=True)
               lines2 = content2.splitlines(keepends=True)
               
               differences = []
               seen = set()
               
               for i, line in enumerate(lines1):
                   if line not in lines2 and line not in seen:
                       differences.append((i, line))
                       seen.add(line)
               
               for i, line in enumerate(lines2):
                   if line not in lines1 and line not in seen:
                       differences.append((i, line))
                       seen.add(line)
               
               differences.sort(key=lambda x: x[0])
               
               with open(output_path, 'w', encoding=enc) as out:
                   for _, line in differences:
                       out.write(line)
               return
       except UnicodeError:
           continue
   raise Exception("Could not read files with any supported encoding")

if __name__ == "__main__":
   file1 = input("Enter first file path: ")
   file2 = input("Enter second file path: ")
   output = input("Enter output file path: ")
   
   try:
       compare_files(file1, file2, output)
       print(f"Differences written to {output}")
   except Exception as e:
       print(f"Error: {e}")