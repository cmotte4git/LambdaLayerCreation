import os
import subprocess
import zipfile
import shutil
import sys
import boto3
from dotenv import load_dotenv

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

load_dotenv('s3.env')
layer_name = "duckdb_layer"  # Desired name for the Lambda layer zip
s3_key = 'duckdb_layer.zip'
runtimes = ["python3.12"]
s3_bucket = os.getenv('S3_BUCKET')
region = os.getenv('AWS_REGION')

publish_layer(layer_name,s3_bucket,s3_key, runtimes, region)