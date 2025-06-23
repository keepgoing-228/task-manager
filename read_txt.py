import sys
import time

# check if the file path and language are provided
if len(sys.argv) != 3:
    print("Please provide the file path and language")
    print("Usage: python read_txt.py <file_path> <language>")
    sys.exit(1)

# get the file path and language
file_path = sys.argv[1]
language = sys.argv[2]

print(f"Processing file: {file_path} with language: {language}")

try:
    # open and read the file
    with open(file_path, "r") as f:
        # read line by line and print
        for line in f:
            print(f"[{language}] {line.strip()}")
            time.sleep(0.5)
except FileNotFoundError:
    print(f"Error: File not found: {file_path}")
except Exception as e:
    print(f"Error: {e}")
