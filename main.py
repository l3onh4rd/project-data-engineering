import pandas as pd
import boto3
import os
import urllib.parse

s3 = boto3.client("s3")


def lambda_handler(event, context):
    print("### Lambda started ###")
    print("### Lambda started THROUGH CODE PIPELINE###")

    try:
        # ---------------------------
        # 1. Event Parsing (robust)
        # ---------------------------
        record = event["Records"][0]

        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        print(f"INPUT BUCKET: {bucket}")
        print(f"INPUT KEY: {key}")

        # ---------------------------
        # 2. Paths
        # ---------------------------
        filename = key.split("/")[-1]

        download_path = f"/tmp/{filename}"
        output_path = "/tmp/output.parquet"

        print(f"DOWNLOAD PATH: {download_path}")
        print(f"OUTPUT PATH: {output_path}")

        # ---------------------------
        # 3. Download CSV
        # ---------------------------
        print("Downloading file from S3...")
        s3.download_file(bucket, key, download_path)
        print("Download complete")

        # ---------------------------
        # 4. CSV → DataFrame
        # ---------------------------
        print("Reading CSV...")
        df = pd.read_csv(download_path)

        print("DF SHAPE:", df.shape)
        print("DF COLUMNS:", df.columns.tolist())

        # ---------------------------
        # 5. Write Parquet
        # ---------------------------
        print("Writing Parquet...")
        df.to_parquet(output_path, index=False, engine="pyarrow")
        print("Parquet written successfully")

        # ---------------------------
        # 6. Output S3 config
        # ---------------------------
        output_bucket = os.environ.get("OUTPUT_BUCKET")

        if not output_bucket:
            raise Exception("OUTPUT_BUCKET environment variable not set")

        output_key = key.replace(".csv", ".parquet")

        print(f"OUTPUT BUCKET: {output_bucket}")
        print(f"OUTPUT KEY: {output_key}")

        # ---------------------------
        # 7. Upload
        # ---------------------------
        print("Uploading to S3...")

        s3.upload_file(
            output_path,
            output_bucket,
            output_key
        )

        print("Upload complete")
        print("### Lambda finished successfully ###")

        return {
            "statusCode": 200,
            "body": "success"
        }

    except Exception as e:
        print("### ERROR OCCURRED ###")
        print(str(e))
        raise e