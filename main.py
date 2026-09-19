import pandas as pd
import boto3
import os
import urllib.parse

s3 = boto3.client("s3")
# constant for expected columns of csv
EXPECTED_COLUMNS = [
    "id",
    "receipt_id",
    "street",
    "zipcode",
    "date",
    "time",
    "product_name",
    "unit_price",
    "quantity",
    "total_price"
]

def lambda_handler(event, context):
    print('Starting Lambda')

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

        # Step 5 - Schema Validation
        print("Validating schema...")

        missing_columns = [
            column
            for column in EXPECTED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        # Step 6 - Preprocessing
        # String Columns

        df["street"] = (
            df["street"]
            .astype("string")
            .str.strip()
        )

        df["product_name"] = (
            df["product_name"]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.upper()
        )

        # ZIP column
        df["zipcode"] = (pd.to_numeric(
            df["zipcode"],
            errors="coerce")
            .astype("Int64"))

        # numeric columns

        df["id"] = pd.to_numeric(
            df["id"],
            errors="coerce"
        )

        df["receipt_id"] = pd.to_numeric(
            df["receipt_id"],
            errors="coerce"
        )

        df["unit_price"] = pd.to_numeric(
            df["unit_price"],
            errors="coerce"
        )

        df["quantity"] = pd.to_numeric(
            df["quantity"],
            errors="coerce"
        )

        df["total_price"] = pd.to_numeric(
            df["total_price"],
            errors="coerce"
        )

        # date and time  column
        df["date"] = pd.to_datetime(
            df["date"],
            format="%d.%m.%Y",
            errors="coerce"
        ).dt.strftime("%d.%m.%Y")

        df["time"] = pd.to_datetime(
            df["time"],
            format="%H:%M:%S",
            errors="coerce"
        ).dt.strftime("%H:%M:%S")

        # Step 7 - Validity Checks
        # Missing Values
        missing_values = (
            df[EXPECTED_COLUMNS]
            .isna()
            .sum()
        )

        invalid_missing = (
            missing_values[
                missing_values > 0
            ]
        )

        # unique ids
        duplicate_ids = df["id"].duplicated().sum()

        if duplicate_ids > 0:

            raise ValueError(
                f"Duplicate IDs detected: {duplicate_ids}"
            )

        if not invalid_missing.empty:

            raise ValueError(
                f"Missing values detected: {str(invalid_missing.to_dict())}"
            )

        # Quantity, Prices, ZIP Code
        invalid_quantity = (
            (df["quantity"] <= 0)
            | (df["quantity"] % 1 != 0)
        )

        if invalid_quantity.any():

            raise ValueError(
                f"Invalid quantity values detected: {invalid_quantity.sum()}"
            )

        invalid_prices = (
            (df["unit_price"] < 0)
            | (df["total_price"] < 0)
        )

        if invalid_prices.any():

            raise ValueError(
                f"Negative prices detected: {invalid_prices.sum()}"
            )

        invalid_zipcodes = ~df["zipcode"].str.match(
            r"^\d{5}$",
            na=False
        )

        if invalid_zipcodes.any():

            raise ValueError(
                f"Invalid ZIP codes detected: {invalid_zipcodes.sum()}"
            )

        # Step 8 - Domain specific validity checks
        expected_total = (
            df["unit_price"]
            * df["quantity"]
        )

        price_difference = (
            (expected_total - df["total_price"])
            .abs()
        )

        invalid_totals = (
            price_difference > 0.01
        )

        if invalid_totals.any():
            print(
                f"Price inconsistencies detected: {invalid_totals.sum()}"
            )
            raise ValueError(
                f"unit_price * quantity does not match total_price for {invalid_totals.sum()} rows"
            )


        # Step 9
        duplicate_rows = df.duplicated().sum()

        if duplicate_rows > 0:

            raise ValueError(
                f"Duplicate rows detected: {duplicate_rows}"
            )

        # Step 10 - Convert to parquet
        df.to_parquet(output_path, index=False, engine="pyarrow")

        # Step 11 - Write parquet file to output bucket
        output_bucket = os.environ.get("OUTPUT_BUCKET")

        if not output_bucket:
            raise Exception("OUTPUT_BUCKET environment variable not set")

        # use original filename without path
        filename = os.path.basename(key)
        # set file type
        parquet_filename = os.path.splitext(filename)[0] + ".parquet"
        # save in subfolder
        output_key = f"parquet/{parquet_filename}"

        # Step 12 - Upload
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