import pandas as pd
import boto3
import os
import urllib.parse
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

s3 = boto3.client("s3")


# util function to save report to S3
def save_report(fig, bucket, key):
    """
    Saves a Plotly figure as a self-contained HTML file
    and uploads it to S3.
    """

    path = "/tmp/shopping_report.html"

    fig.write_html(
        path,
        include_plotlyjs=True,
        full_html=True
    )

    s3.upload_file(
        path,
        bucket,
        key,
        ExtraArgs={
            "ContentType": "text/html"
        }
    )

    print(f"Report created: s3://{bucket}/{key}")


def add_kpi_header(fig, df):
    """
    Adds KPI header to the dashboard.

    KPIs:
    - Total Revenue
    - Number of Purchases
    - Products Purchased
    - Average Basket Value
    """

    # calculate KPIs
    total_revenue = df["total_price"].sum()
    total_products = df["quantity"].sum()
    total_purchases = df["receipt_id"].nunique()

    if total_purchases > 0:
        average_basket = (
            total_revenue / total_purchases
        )
    else:
        average_basket = 0

    # Title of the Dashboard
    fig.add_annotation(
        text="<b>📊 Projekt Data Engineering - Shopping Report 🛒</b>",
        x=0.5,
        y=1.13,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            size=36
        ),
        align="center"
    )
    # KPI Gesamtausgaben
    fig.add_annotation(
        text=(
            f"<b>{total_revenue:,.2f} €</b>"
            "<br>"
            "<span style='font-size:16px'>Gesamtausgaben</span>"
        ),
        x=0.125,
        y=1.1,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(
            size=24
        )
    )
    # KPI Einkäufe Gesamt
    fig.add_annotation(
        text=(
            f"<b>{total_purchases:,}</b>"
            "<br>"
            "<span style='font-size:16px'>Einkäufe Gesamt</span>"
        ),
        x=0.375,
        y=1.1,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(
            size=24
        )
    )
    # KPI Produktkäufe
    fig.add_annotation(
        text=(
            f"<b>{total_products:,}</b>"
            "<br>"
            "<span style='font-size:16px'>Produktkäufe</span>"
        ),
        x=0.625,
        y=1.1,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(
            size=24
        )
    )

    fig.add_annotation(
        text=(
            f"<b>{average_basket:,.2f} €</b>"
            "<br>"
            "<span style='font-size:16px'>Durchschnitt Einkaufswagen</span>"
        ),
        x=0.875,
        y=1.1,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(
            size=24
        )
    )

# 
def create_shopping_report(df, bucket, report_date):
    """
    Adds charts to dashboard.
    """

    # daily spendings
    daily = (
        df.groupby(df["date"].dt.date)
        .agg(
            revenue=("total_price", "sum")
        )
        .reset_index()
    )

    daily["date"] = pd.to_datetime(
        daily["date"]
    )

    # 7 day average
    daily["revenue_ma7"] = (
        daily["revenue"]
        .rolling(
            window=7,
            min_periods=1
        )
        .mean()
    )

    # spendings per receipt
    baskets = (
        df.groupby("receipt_id")
        .agg(
            purchase_date=("date", "first"),
            products=("quantity", "sum"),
            basket_value=("total_price", "sum")
        )
        .reset_index()
    )
    # spendings per product
    products = (
        df.groupby("product_name")
        .agg(
            quantity=("quantity", "sum"),
            revenue=("total_price", "sum")
        )
        .reset_index()
    )
    # top 15 products by quantity
    top_quantity = (
        products
        .sort_values(
            "quantity",
            ascending=False
        )
        .head(15)
        .sort_values("quantity")
    )
    # top 15 products by price
    top_revenue = (
        products
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(15)
        .sort_values("revenue")
    )

    fig = make_subplots(
        rows=4,
        cols=2,
        specs=[
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 2}, None]
        ],
        row_heights=[
            0.22,
            0.22,
            0.28,
            0.28
        ],
        vertical_spacing=0.12,
        subplot_titles=(
            "Tägliche Ausgaben",
            "Ausgaben je Einkauf",
            "Produkte je Einkauf",
            "Top 15 Produkte nach Preis",
            "Top 15 Produkte nach Anzahl"
        )
    )
    # Daily spendings chart
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["revenue"],
            mode="lines",
            name="Tägliche Ausgaben",
            line=dict(
                width=3,
                color="#DE0016"
            ),
            hovertemplate=(
                "%{x|%d.%m.%Y}<br>"
                "<b>Ausgaben:</b> %{y:,.2f} €"
                "<extra></extra>"
            )
        ),
        row=1,
        col=1
    )
    # 7-Day Average
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["revenue_ma7"],
            mode="lines",
            name="7-Tages Durchschnitt",
            line=dict(
                width=2,
                dash="dash",
                color="#3A9970"
            ),
            hovertemplate=(
                "%{x|%d.%m.%Y}<br>"
                "<b>7-Tages Durchschnitt:</b> %{y:,.2f} €"
                "<extra></extra>"
            )
        ),
        row=1,
        col=1
    )
    # x-axis label
    fig.update_xaxes(
        title_text="Datum",
        row=1,
        col=1
    )
    # y-axis label
    fig.update_yaxes(
        title_text="Ausgaben (€)",
        row=1,
        col=1
    )
    # spendings per basket
    fig.add_trace(
        go.Histogram(
            x=baskets["basket_value"],
            nbinsx=30,
            name="Einkaufswagen Wert",
            hovertemplate=(
                "Einkaufswagen Wert: %{x:.2f} €"
                "<br>"
                "Einkäufe: %{y}"
                "<extra></extra>"
            ),
        ),
        row=2,
        col=1
    )

    fig.update_xaxes(
        title_text="Einkaufswagen Wer (€)",
        row=2,
        col=1
    )

    fig.update_yaxes(
        title_text="Anzahl der Einkäufe",
        row=2,
        col=1
    )
    # products per basket
    fig.add_trace(
        go.Histogram(
            x=baskets["products"],
            nbinsx=30,
            name="Produkte je Einkauf",
            hovertemplate=(
                "Produkte: %{x}"
                "<br>"
                "Einkäufe: %{y}"
                "<extra></extra>"
            ),
        ),
        row=2,
        col=2
    )

    fig.update_xaxes(
        title_text="Produkte je Einkauf",
        row=2,
        col=2
    )

    fig.update_yaxes(
        title_text="Anzahl der Einkäufe",
        row=2,
        col=2
    )
    # top 15 products per price
    fig.add_trace(
        go.Bar(
            x=top_revenue["revenue"],
            y=top_revenue["product_name"],
            orientation="h",
            name="Ausgaben",
            hovertemplate=(
                "%{y}<br>"
                "<b>Ausgaben:</b> %{x:,.2f} €"
                "<extra></extra>"
            ),
        ),
        row=3,
        col=1
    )

    fig.update_xaxes(
        title_text="Ausgaben (€)",
        row=3,
        col=1
    )

    fig.update_yaxes(
        title_text="Produkt",
        row=3,
        col=1
    )
    # top 15 products by quantity
    fig.add_trace(
        go.Bar(
            x=top_quantity["quantity"],
            y=top_quantity["product_name"],
            orientation="h",
            name="Anzahl",
            hovertemplate=(
                "%{y}<br>"
                "<b>Anzahl:</b> %{x:,}"
                "<extra></extra>"
            ),
        ),
        row=4,
        col=1
    )

    fig.update_xaxes(
        title_text="Anzahl",
        row=4,
        col=1
    )

    fig.update_yaxes(
        title_text="Produkt",
        row=4,
        col=1
    )

    # dashboard layout
    fig.update_layout(
        height=1950,
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                size=13
            )
        ),

        margin=dict(
            l=90,
            r=90,
            t=270,
            b=80
        ),

        font=dict(
            size=13
        ),

        hovermode="closest"
    )

    # add kpi headline
    add_kpi_header(
        fig,
        df
    )

    # save report as html
    key = (
        f"reports/{report_date}/"
        f"shopping_report.html"
    )

    save_report(
        fig,
        bucket,
        key
    )

# main lambda handler
def lambda_handler(event, context):

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
        print("DF SIZE:", df.size)

        # Step 5 - Prepare data
        df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")

        products_per_day = (
            df.groupby(df["date"].dt.date)["quantity"]
            .sum()
            .reset_index()
        )

        products_per_day.columns = [
            "date",
            "products"
        ]
        # Step 6 - Create timestamp
        report_date = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        # Step 7 - create dashboard report
        create_shopping_report(
            df,
            report_bucket,
            report_date
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