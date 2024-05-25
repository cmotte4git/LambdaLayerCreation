import os
import subprocess
import zipfile
import shutil
import sys
from dotenv import load_dotenv

def download_wheel(package_name, platform, destination_dir):
    try:
        # Download the package wheel file
        subprocess.check_call([
            sys.executable,
            "-m", "pip", "download",
            "--only-binary", ":all:",
            "--dest", destination_dir,
            "--no-cache",
            "--platform", platform,
            package_name
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while downloading {package_name} wheel file: {e}")
        sys.exit(1)

def extract_whl(whl_file, destination_dir):
    # Extract the .whl file into the destination directory
    with zipfile.ZipFile(whl_file, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)

def create_layer_zip(layer_name, source_dir):
    zip_path = f"{layer_name}.zip"
    
    # Create a zip file with the 'python' directory
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, source_dir))

    print(f"{zip_path} created successfully.")
    return zip_path

if __name__ == "__main__":
   
    package_name = "duckdb"  # Replace with the package you need
    platform = "manylinux_2_24_aarch64"  # Platform for the wheel file
    layer_name = "duckdb_layer"  # Desired name for the Lambda layer zip
    source_dir = "lambda_layer/python"  # Source directory containing the files for the Lambda layer

    # Create the lambda_layer/python directory if it doesn't exist
    os.makedirs(source_dir, exist_ok=True)

    # Download the .whl file
    download_wheel(package_name, platform, source_dir)

    # Extract the .whl file into the python directory
    whl_files = [f for f in os.listdir(source_dir) if f.endswith(".whl")]
    if not whl_files:
        print("No wheel files found.")
        sys.exit(1)

    for whl_file in whl_files:
        whl_path = os.path.join(source_dir, whl_file)
        extract_whl(whl_path, source_dir)
        os.remove(whl_path)  # Remove the .whl file

    # Create the Lambda layer zip file
    zip_path = create_layer_zip(layer_name, os.path.dirname(source_dir))
