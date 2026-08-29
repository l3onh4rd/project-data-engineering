import pandas as pd
import boto3
import os
import urllib.parse

s3 = boto3.client("s3")


def lambda_handler(event, context):
    # print('42 Hello Report 42')

    try:
        # Step 1 - Parse Event
        record = event["Records"][0]

        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        # Step 2 - Parse paths
        filename = key.split("/")[-1]

        download_path = f"/tmp/{filename}"
        # output_path = "/tmp/output.parquet"

        # # Step 3 - Download File
        s3.download_file(bucket, key, download_path)

        # # Step 4 - Read Parquet
        print("Reading CSV...")
        df = pd.read_parquet(download_path)
        # Printing Debugging Information
        print("DF SHAPE:", df.shape)
        print("DF COLUMNS:", df.columns.tolist())
        print("DF COLUMNS:", df.size)

        # Step 7 - Upload
        # s3.upload_file(
        #     output_path,
        #     output_bucket,
        #     output_key
        # )

        print("### Lambda finished successfully ###")

        return {
            "statusCode": 200,
            "body": "success"
        }

    except Exception as e:
        print("### ERROR OCCURRED ###")
        print(str(e))
        raise e