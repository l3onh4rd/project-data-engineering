import pandas as pd
import boto3
import os
import urllib.parse
# import plotly.express as px
from datetime import datetime

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

        # Report Bucket
        report_bucket = os.environ["REPORT_BUCKET"]
        # output_path = "/tmp/output.parquet"

        # # Step 3 - Download File
        s3.download_file(bucket, key, download_path)

        # # Step 4 - Read Parquet
        print("Reading Parquet...")
        df = pd.read_parquet(download_path)
        # Printing Debugging Information
        print("DF SHAPE:", df.shape)
        print("DF COLUMNS:", df.columns.tolist())
        print("DF COLUMNS:", df.size)

        # Step 5 - Prepare data
        df["date"] = pd.to_datetime(df["date"])

        products_per_day = (
            df.groupby(df["date"].dt.date)["quantity"]
            .sum()
            .reset_index()
        )

        products_per_day.columns = [
            "date",
            "products"
        ]

        print("Products per day:")
        print(products_per_day)

        # # Step 6 - Create Plotly chart
        # fig = px.bar(
        #     products_per_day,
        #     x="date",
        #     y="products",
        #     title="Anzahl gekaufter Produkte pro Tag",
        #     labels={
        #         "date": "Datum",
        #         "products": "Gekaufte Produkte"
        #     }
        # )


        # # Step 7 - Create timestamped filename
        # timestamp = datetime.now().strftime(
        #     "%Y-%m-%d_%H-%M-%S"
        # )

        # chart_filename = f"products-per-day_{timestamp}.png"

        # chart_path = f"/tmp/{chart_filename}"

        # # Step 8 - Save HTML
        # fig.write_html(
        #     chart_path,
        #     include_plotlyjs=True
        # )

        # # Step 9 - Upload to S3
        # report_key = f"charts/{chart_filename}"

        # s3.upload_file(
        #     chart_path,
        #     report_bucket,
        #     report_key,
        #     ExtraArgs={
        #         "ContentType": "text/html"
        #     }
        # )

        # print(
        #     f"Chart successfully uploaded to "
        #     f"s3://{report_bucket}/{report_key}"
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