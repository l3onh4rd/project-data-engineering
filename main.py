import pandas as pd
import boto3
import os
import urllib.parse

s3 = boto3.client("s3")


def lambda_handler(event, context):
    # print('42 Hello World 42')

    try:
        # Step 1 - Parse Event
        record = event["Records"][0]

        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        # Step 2 - Parse paths
        filename = key.split("/")[-1]

        download_path = f"/tmp/{filename}"
        output_path = "/tmp/output.parquet"

        # Step 3 - Download File
        s3.download_file(bucket, key, download_path)

        # Step 4 - Read CSV
        print("Reading CSV...")
        df = pd.read_csv(download_path)
        # Printing Debugging Information
        print("DF SHAPE:", df.shape)
        print("DF COLUMNS:", df.columns.tolist())

        # Step 5 - Convert to parquet
        df.to_parquet(output_path, index=False, engine="pyarrow")

        # Step 6 - Write parquet file to output bucket
        output_bucket = os.environ.get("OUTPUT_BUCKET")

        if not output_bucket:
            raise Exception("OUTPUT_BUCKET environment variable not set")

        # use original filename without path
        filename = os.path.basename(key)
        # set file type
        parquet_filename = os.path.splitext(filename)[0] + ".parquet"
        # save in subfolder
        output_key = f"parquet/{parquet_filename}"

        # Step 7 - Upload
        s3.upload_file(
            output_path,
            output_bucket,
            output_key
        )

        print("### Lambda finished successfully ###")

        return {
            "statusCode": 200,
            "body": "success"
        }

    except Exception as e:
        print("### ERROR OCCURRED ###")
        print(str(e))
        raise e