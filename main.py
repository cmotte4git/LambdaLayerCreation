import os
import subprocess
import zipfile
import shutil
import sys
import boto3
import boto3
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

def upload_s3(file_obj, s3_bucket, s3_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('S3_ACCESS'),
        aws_secret_access_key=os.getenv('S3_SECRET')
    )
    s3.upload_file(file_obj, s3_bucket, s3_key)
    print(f"Uploaded {file_obj} to s3://{s3_bucket}/{s3_key}")

def publish_layer(layer_name, s3_bucket, s3_key, runtimes, region):
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=os.getenv('S3_ACCESS'),
        aws_secret_access_key=os.getenv('S3_SECRET'),
        region_name=region
    )
    response = lambda_client.publish_layer_version(
        LayerName=layer_name,
        Content={
            'S3Bucket': s3_bucket,
            'S3Key': s3_key
        }
        ,
        CompatibleRuntimes=runtimes
    )
    print(f"Published layer version ARN: {response['LayerVersionArn']}")

if __name__ == "__main__":
    # Load environment variables from the .env file
    load_dotenv('s3.env')
    
    package_name = "duckdb"  # Replace with the package you need
    platform = "manylinux_2_24_aarch64"  # Platform for the wheel file
    layer_name = "duckdb_layer"  # Desired name for the Lambda layer zip
    source_dir = "lambda_layer/python"  # Source directory containing the files for the Lambda layer
    runtimes = ["python3.12"]
    region = os.getenv('AWS_REGION')

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

    if zip_path:
        # Upload the zip file to S3
        s3_bucket = os.getenv('S3_BUCKET')
        s3_key = zip_path
        upload_s3(zip_path, s3_bucket, s3_key)

        #Publish the layer
        publish_layer(layer_name,s3_bucket,s3_key, runtimes, region)
    
    #clean files
    shutil.rmtree(source_dir)
    os.remove(zip_path)