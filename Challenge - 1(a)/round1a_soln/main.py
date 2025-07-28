# main.py

from extractor.runner import process_pdfs_in_directory

if __name__ == "__main__":
    process_pdfs_in_directory(input_dir="input", output_dir="output")
