# project-data-engineering

This project implements a cloud-based data engineering pipeline for processing and analysing supermarket purchase data.

The project demonstrates the ingestion, transformation, validation, storage and analysis of a large purchase dataset containing approximately 1.5 million records.

## Architecture

The pipeline is implemented using AWS services:
S3, AWS Lambda, Cloud Formation, Code Pipeline, Code Build, Glue, Athena

The infrastructure is defined using AWS CloudFormation.

## Data Processing

The transformation Lambda (main.py) processes the raw CSV data and performs:

- schema validation
- data type conversion
- missing-value checks
- validation of prices and quantities
- date and time processing
- text normalization
- CSV to Parquet conversion

The processed data is stored in Amazon S3 in Parquet format.

The dataset contains information such as:

- id
- receipt_id
- street
- zipcode
- date
- time
- product_name
- unit_price
- quantity
- total_price

A second Lambda function (report.py) generates a self-contained interactive HTML report using Plotly.

The report contains:

- KPI overview
- Daily Spendings
- Average 7-Day Spendings
- Spendings per purchase
- Products per purchase
- Top 15 Products by Price
- Top 15 Products by Quantity

Reports are stored in S3 using a date-based structure.

## Deployment
The infrastructure can be deployed using AWS CloudFormation. After deployment, uploading a CSV file to the configured input S3 bucket starts the data processing pipeline.

The resulting Parquet data is stored in the output bucket and can be queried using Athena. The reporting Lambda subsequently generates the interactive HTML report.

### Step-by-step guide to deploy the infrastructure

- Step 0
    - Go to your aws console and create a CloudFormation stack.
- Step 1
    - Copy the stack.yaml file to your CloudFormation template editor.
    - Deploy the stack with no changes to the script. Leave all commented out sections as they are.
    - Deploy the stack.
- Step 2
    - After the successful deployment of step 1 you need to:
    - Upload the function.zip to the created lambda-code-deployment S3 bucket.
    - Upload the report.zip file to the created lambda-report-deployment S3 bucket.
    - Remove the commented section of the stack.yaml for step 2 (until the comment 'END STEP 2')
    - Deploy the stack.
- Step 3
    - Remove the commented section marked with STEP 3. Activate the NotificationConfiguration for the S3 Buckets input and output.
    - Deploy the stack.
- Step 4
    - Remove the commented section marked with STEP 4 (until the comment 'END STEP 4').
    - Deploy the stack. It deploys the build pipeline.
    - After successful deployment you need to authorize the github connection once via the aws console in the CodePipeline service under 'connections'.
- Step 5
    - Deploy the rest of the stack.yaml file and the last steps for the aws athena and aws glue servics will be deployed.

Now the complete infrastructure is deployed and ready to use.

## Technologies
- Python
- Pandas
- PyArrow
- Plotly
- AWS Lambda
- Amazon S3
- AWS Glue
- Amazon Athena
- AWS CloudFormation
- AWS CodeBuild
- AWS CodePipeline
- GitHub

## Purpose

The project serves as a practical implementation of a batch-oriented data engineering pipeline and demonstrates how large-scale transactional data can be transformed, validated, stored in a columnar format and made available for analytical processing in a cloud environment.