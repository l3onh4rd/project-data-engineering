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