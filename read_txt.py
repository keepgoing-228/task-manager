import sys
import time

# check if the file path is provided
if len(sys.argv) != 2:
    print("Please provide the file path")
    print("Usage: python read_txt.py <file_path>")
    sys.exit(1)

# get the file path
file_path = sys.argv[1]

try:
    # open and read the file
    with open(file_path, "r") as f:
        # read line by line and print
        for line in f:
            print(line.strip())
            time.sleep(0.5)
except FileNotFoundError:
    print(f"Error: File not found: {file_path}")
except Exception as e:
    print(f"Error: {e}")
