import pandas as pd
import boto3
import os

s3 = boto3.client("s3")

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    download_path = f"/tmp/{key.split('/')[-1]}"
    upload_path = download_path.replace(".csv", ".parquet")

    s3.download_file(bucket, key, download_path)

    df = pd.read_csv(download_path)
    df.to_parquet(upload_path, index=False)

    output_bucket = os.environ["OUTPUT_BUCKET"]

    s3.upload_file(upload_path, output_bucket, key.replace(".csv", ".parquet"))

    return {"status": "success"}