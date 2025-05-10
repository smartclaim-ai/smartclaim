#!/usr/bin/env python3
# Insurance Claims Data Analysis Script

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import calendar
import io
import sys
from contextlib import redirect_stdout

# Set plot styles
sns.set(style="whitegrid")
plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (12, 8)


# Create a class to capture stdout
class CaptureOutput:
    def __init__(self):
        self.output = io.StringIO()
        self.stdout_redirector = redirect_stdout(self.output)

    def __enter__(self):
        self.stdout_redirector.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stdout_redirector.__exit__(exc_type, exc_val, exc_tb)

    def get_output(self):
        return self.output.getvalue()


def load_data(file_path="data/minimized_data.csv"):
    """
    Load the insurance claims dataset
    """
    print(f"Loading insurance claims data from {file_path}...")
    df = pd.read_csv(file_path)

    # Convert CLAIM_DATE to datetime
    df["CLAIM_DATE"] = pd.to_datetime(df["CLAIM_DATE"], format="%d/%m/%Y")

    # Extract useful date features
    df["CLAIM_YEAR"] = df["CLAIM_DATE"].dt.year
    df["CLAIM_MONTH"] = df["CLAIM_DATE"].dt.month
    df["CLAIM_MONTH_NAME"] = df["CLAIM_DATE"].dt.month_name()
    df["CLAIM_DAY"] = df["CLAIM_DATE"].dt.day
    df["CLAIM_WEEKDAY"] = df["CLAIM_DATE"].dt.day_name()
    df["CLAIM_QUARTER"] = df["CLAIM_DATE"].dt.quarter

    # Calculate Age Groups for easier analysis
    bins = [0, 25, 35, 45, 55, 65, 75, 100]
    labels = ["<25", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"]
    df["AGE_GROUP"] = pd.cut(
        df["POLICYHOLDER_AGE"], bins=bins, labels=labels, right=False
    )

    # Calculate Loss Ratio (claim amount / premium amount)
    df["LOSS_RATIO"] = df["CLAIM_AMOUNT_PAID"] / df["PREMIUM_AMOUNT_PAID"]

    return df


def explore_data(df, sample_size=5):
    """
    Explore the insurance claims dataset structure and statistics
    """
    print("\n==== INSURANCE CLAIMS DATA EXPLORATION ====")
    print(f"\nDataset shape: {df.shape} (rows, columns)")
    print(f"\nFirst {sample_size} rows:")
    print(df.head(sample_size))

    print("\nBasic statistics of numerical variables:")
    print(
        df[
            [
                "POLICYHOLDER_AGE",
                "CLAIM_AMOUNT_PAID",
                "PREMIUM_AMOUNT_PAID",
                "LOSS_RATIO",
            ]
        ].describe()
    )

    print("\nValue counts for WARRANTY types:")
    print(df["WARRANTY"].value_counts())

    print("\nValue counts for VEHICLE_BRAND:")
    print(df["VEHICLE_BRAND"].value_counts().head(10))

    print("\nValue counts for AGE_GROUP:")
    print(df["AGE_GROUP"].value_counts())

    print("\nValue counts for CLAIM_REGION:")
    print(df["CLAIM_REGION"].value_counts().head(10))

    print("\nMissing values per column:")
    print(df.isnull().sum())


def analyze_claims_by_warranty(df):
    """
    Analyze claims by warranty type
    """
    print("\n==== CLAIMS ANALYSIS BY WARRANTY TYPE ====")

    # Create directory for visualizations
    Path("visualizations").mkdir(exist_ok=True)

    # Group by WARRANTY and calculate key metrics
    warranty_analysis = (
        df.groupby("WARRANTY")
        .agg(
            {
                "CLAIM_ID": "count",
                "CLAIM_AMOUNT_PAID": ["mean", "sum", "median"],
                "PREMIUM_AMOUNT_PAID": ["mean", "sum"],
                "LOSS_RATIO": ["mean", "median"],
            }
        )
        .sort_values(("CLAIM_ID", "count"), ascending=False)
    )

    warranty_analysis.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Median_Claim_Amount",
        "Avg_Premium",
        "Total_Premium",
        "Avg_Loss_Ratio",
        "Median_Loss_Ratio",
    ]

    print("\nWarranty Analysis Summary:")
    print(warranty_analysis.reset_index())

    # Visualize Claims by Warranty Type
    plt.figure(figsize=(14, 7))
    top_warranties = df["WARRANTY"].value_counts().head(8).index
    warranty_df = df[df["WARRANTY"].isin(top_warranties)]

    plt.subplot(1, 2, 1)
    sns.countplot(
        data=warranty_df,
        x="WARRANTY",
        order=warranty_df["WARRANTY"].value_counts().index,
    )
    plt.title("Number of Claims by Warranty Type")
    plt.xlabel("Warranty Type")
    plt.ylabel("Number of Claims")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(1, 2, 2)
    sns.boxplot(
        data=warranty_df,
        x="WARRANTY",
        y="CLAIM_AMOUNT_PAID",
        order=warranty_df["WARRANTY"].value_counts().index,
    )
    plt.title("Claim Amount Distribution by Warranty Type")
    plt.xlabel("Warranty Type")
    plt.ylabel("Claim Amount (€)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig("visualizations/warranty_analysis.png")
    print(
        "Saved warranty analysis visualization to visualizations/warranty_analysis.png"
    )

    return warranty_analysis


def analyze_claims_by_demographics(df):
    """
    Analyze claims by policyholder demographics (age and gender)
    """
    print("\n==== CLAIMS ANALYSIS BY DEMOGRAPHICS ====")

    # Gender analysis
    gender_analysis = df.groupby("POLICYHOLDER_GENDER").agg(
        {
            "CLAIM_ID": "count",
            "CLAIM_AMOUNT_PAID": ["mean", "sum", "median"],
            "PREMIUM_AMOUNT_PAID": ["mean", "sum"],
            "LOSS_RATIO": ["mean", "median"],
        }
    )

    gender_analysis.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Median_Claim_Amount",
        "Avg_Premium",
        "Total_Premium",
        "Avg_Loss_Ratio",
        "Median_Loss_Ratio",
    ]

    print("\nGender Analysis Summary:")
    print(gender_analysis.reset_index())

    # Age group analysis
    age_analysis = df.groupby("AGE_GROUP").agg(
        {
            "CLAIM_ID": "count",
            "CLAIM_AMOUNT_PAID": ["mean", "sum", "median"],
            "PREMIUM_AMOUNT_PAID": ["mean", "sum"],
            "LOSS_RATIO": ["mean", "median"],
        }
    )

    age_analysis.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Median_Claim_Amount",
        "Avg_Premium",
        "Total_Premium",
        "Avg_Loss_Ratio",
        "Median_Loss_Ratio",
    ]

    print("\nAge Group Analysis Summary:")
    print(age_analysis.reset_index())

    # Age & Gender Combined
    plt.figure(figsize=(16, 10))

    plt.subplot(2, 2, 1)
    sns.countplot(data=df, x="AGE_GROUP", hue="POLICYHOLDER_GENDER")
    plt.title("Number of Claims by Age Group and Gender")
    plt.xlabel("Age Group")
    plt.ylabel("Number of Claims")

    plt.subplot(2, 2, 2)
    sns.boxplot(data=df, x="AGE_GROUP", y="CLAIM_AMOUNT_PAID")
    plt.title("Claim Amount by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Claim Amount (€)")

    plt.subplot(2, 2, 3)
    age_amount = df.groupby("AGE_GROUP")["CLAIM_AMOUNT_PAID"].mean().reset_index()
    sns.barplot(data=age_amount, x="AGE_GROUP", y="CLAIM_AMOUNT_PAID")
    plt.title("Average Claim Amount by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Average Claim Amount (€)")

    plt.subplot(2, 2, 4)
    age_gender_amount = (
        df.groupby(["AGE_GROUP", "POLICYHOLDER_GENDER"])["CLAIM_AMOUNT_PAID"]
        .mean()
        .reset_index()
    )
    sns.barplot(
        data=age_gender_amount,
        x="AGE_GROUP",
        y="CLAIM_AMOUNT_PAID",
        hue="POLICYHOLDER_GENDER",
    )
    plt.title("Average Claim Amount by Age Group and Gender")
    plt.xlabel("Age Group")
    plt.ylabel("Average Claim Amount (€)")

    plt.tight_layout()
    plt.savefig("visualizations/demographic_analysis.png")
    print(
        "Saved demographic analysis visualization to visualizations/demographic_analysis.png"
    )

    return gender_analysis, age_analysis


def analyze_claims_by_vehicle(df):
    """
    Analyze claims by vehicle characteristics (brand and model)
    """
    print("\n==== CLAIMS ANALYSIS BY VEHICLE ====")

    # Top vehicle brands by claim count
    top_brands = df["VEHICLE_BRAND"].value_counts().head(10)
    print("\nTop 10 Vehicle Brands by Claim Count:")
    print(top_brands)

    # Top brands by average claim amount
    brand_claims = (
        df.groupby("VEHICLE_BRAND")
        .agg(
            {
                "CLAIM_ID": "count",
                "CLAIM_AMOUNT_PAID": ["mean", "sum", "median"],
                "LOSS_RATIO": "mean",
            }
        )
        .sort_values(("CLAIM_ID", "count"), ascending=False)
        .head(15)
    )

    brand_claims.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Median_Claim_Amount",
        "Avg_Loss_Ratio",
    ]
    print("\nTop 15 Vehicle Brands Analysis:")
    print(brand_claims.reset_index())

    # Vehicle brand visualization
    plt.figure(figsize=(16, 10))

    plt.subplot(2, 2, 1)
    top_10_brands = df["VEHICLE_BRAND"].value_counts().head(10).index
    brand_df = df[df["VEHICLE_BRAND"].isin(top_10_brands)]
    sns.countplot(
        data=brand_df,
        x="VEHICLE_BRAND",
        order=brand_df["VEHICLE_BRAND"].value_counts().index,
    )
    plt.title("Number of Claims by Vehicle Brand (Top 10)")
    plt.xlabel("Vehicle Brand")
    plt.ylabel("Number of Claims")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(2, 2, 2)
    sns.boxplot(
        data=brand_df,
        x="VEHICLE_BRAND",
        y="CLAIM_AMOUNT_PAID",
        order=brand_df["VEHICLE_BRAND"].value_counts().index,
    )
    plt.title("Claim Amount Distribution by Vehicle Brand (Top 10)")
    plt.xlabel("Vehicle Brand")
    plt.ylabel("Claim Amount (€)")
    plt.xticks(rotation=45, ha="right")

    # Brand and warranty type correlation
    plt.subplot(2, 2, 3)
    top_5_brands = df["VEHICLE_BRAND"].value_counts().head(5).index
    top_5_warranties = df["WARRANTY"].value_counts().head(5).index
    brand_warranty_df = df[
        df["VEHICLE_BRAND"].isin(top_5_brands) & df["WARRANTY"].isin(top_5_warranties)
    ]

    brand_warranty_counts = pd.crosstab(
        brand_warranty_df["VEHICLE_BRAND"], brand_warranty_df["WARRANTY"]
    )
    brand_warranty_pct = brand_warranty_counts.div(
        brand_warranty_counts.sum(axis=1), axis=0
    )
    sns.heatmap(brand_warranty_pct, annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title("Warranty Type Distribution by Vehicle Brand (Top 5 Each)")
    plt.xlabel("Warranty Type")
    plt.ylabel("Vehicle Brand")

    # Brand by average claim amount
    plt.subplot(2, 2, 4)
    brand_avg_claim = (
        brand_df.groupby("VEHICLE_BRAND")["CLAIM_AMOUNT_PAID"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    sns.barplot(data=brand_avg_claim, x="VEHICLE_BRAND", y="CLAIM_AMOUNT_PAID")
    plt.title("Average Claim Amount by Vehicle Brand (Top 10)")
    plt.xlabel("Vehicle Brand")
    plt.ylabel("Average Claim Amount (€)")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig("visualizations/vehicle_analysis.png")
    print("Saved vehicle analysis visualization to visualizations/vehicle_analysis.png")

    return brand_claims


def analyze_claims_by_geography(df):
    """
    Analyze claims by geographical characteristics (region and province)
    """
    print("\n==== CLAIMS ANALYSIS BY GEOGRAPHY ====")

    # Region analysis
    region_analysis = (
        df.groupby("CLAIM_REGION")
        .agg(
            {
                "CLAIM_ID": "count",
                "CLAIM_AMOUNT_PAID": ["mean", "sum", "median"],
                "PREMIUM_AMOUNT_PAID": ["mean", "sum"],
                "LOSS_RATIO": ["mean", "median"],
            }
        )
        .sort_values(("CLAIM_ID", "count"), ascending=False)
    )

    region_analysis.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Median_Claim_Amount",
        "Avg_Premium",
        "Total_Premium",
        "Avg_Loss_Ratio",
        "Median_Loss_Ratio",
    ]

    print("\nTop Regions by Claim Count:")
    print(region_analysis.head(10).reset_index())

    # Visualize regional data
    plt.figure(figsize=(14, 10))

    plt.subplot(2, 2, 1)
    top_regions = df["CLAIM_REGION"].value_counts().head(10).index
    region_df = df[df["CLAIM_REGION"].isin(top_regions)]
    sns.countplot(
        data=region_df,
        x="CLAIM_REGION",
        order=region_df["CLAIM_REGION"].value_counts().index,
    )
    plt.title("Number of Claims by Region (Top 10)")
    plt.xlabel("Region")
    plt.ylabel("Number of Claims")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(2, 2, 2)
    region_avg_claim = (
        region_df.groupby("CLAIM_REGION")["CLAIM_AMOUNT_PAID"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    sns.barplot(data=region_avg_claim, x="CLAIM_REGION", y="CLAIM_AMOUNT_PAID")
    plt.title("Average Claim Amount by Region (Top 10)")
    plt.xlabel("Region")
    plt.ylabel("Average Claim Amount (€)")
    plt.xticks(rotation=45, ha="right")

    # Warranty type distribution by region
    plt.subplot(2, 2, 3)
    top_5_regions = df["CLAIM_REGION"].value_counts().head(5).index
    top_5_warranties = df["WARRANTY"].value_counts().head(5).index
    region_warranty_df = df[
        df["CLAIM_REGION"].isin(top_5_regions) & df["WARRANTY"].isin(top_5_warranties)
    ]

    region_warranty_counts = pd.crosstab(
        region_warranty_df["CLAIM_REGION"], region_warranty_df["WARRANTY"]
    )
    region_warranty_pct = region_warranty_counts.div(
        region_warranty_counts.sum(axis=1), axis=0
    )
    sns.heatmap(region_warranty_pct, annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title("Warranty Type Distribution by Region (Top 5 Each)")
    plt.xlabel("Warranty Type")
    plt.ylabel("Region")

    # Loss ratio by region
    plt.subplot(2, 2, 4)
    region_loss_ratio = (
        region_df.groupby("CLAIM_REGION")["LOSS_RATIO"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    sns.barplot(data=region_loss_ratio, x="CLAIM_REGION", y="LOSS_RATIO")
    plt.title("Average Loss Ratio by Region (Top 10)")
    plt.xlabel("Region")
    plt.ylabel("Loss Ratio (Claim/Premium)")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig("visualizations/geography_analysis.png")
    print(
        "Saved geography analysis visualization to visualizations/geography_analysis.png"
    )

    return region_analysis


def analyze_temporal_patterns(df):
    """
    Analyze temporal patterns in claims data
    """
    print("\n==== TEMPORAL PATTERNS ANALYSIS ====")

    # Claims by month
    monthly_claims = df.groupby("CLAIM_MONTH_NAME").agg(
        {
            "CLAIM_ID": "count",
            "CLAIM_AMOUNT_PAID": ["mean", "sum"],
            "LOSS_RATIO": "mean",
        }
    )

    # Reorder months correctly
    month_order = list(calendar.month_name)[1:]
    monthly_claims = monthly_claims.reindex(month_order)

    monthly_claims.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Avg_Loss_Ratio",
    ]
    print("\nClaims by Month:")
    print(monthly_claims.reset_index())

    # Claims by quarter
    quarterly_claims = df.groupby("CLAIM_QUARTER").agg(
        {
            "CLAIM_ID": "count",
            "CLAIM_AMOUNT_PAID": ["mean", "sum"],
            "LOSS_RATIO": "mean",
        }
    )

    quarterly_claims.columns = [
        "Claim_Count",
        "Avg_Claim_Amount",
        "Total_Claim_Amount",
        "Avg_Loss_Ratio",
    ]
    print("\nClaims by Quarter:")
    print(quarterly_claims.reset_index())

    # Visualize temporal patterns
    plt.figure(figsize=(16, 12))

    plt.subplot(2, 2, 1)
    month_count = (
        df.groupby("CLAIM_MONTH_NAME")["CLAIM_ID"]
        .count()
        .reindex(month_order)
        .reset_index()
    )
    sns.barplot(data=month_count, x="CLAIM_MONTH_NAME", y="CLAIM_ID")
    plt.title("Number of Claims by Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Claims")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(2, 2, 2)
    month_amount = (
        df.groupby("CLAIM_MONTH_NAME")["CLAIM_AMOUNT_PAID"]
        .mean()
        .reindex(month_order)
        .reset_index()
    )
    sns.barplot(data=month_amount, x="CLAIM_MONTH_NAME", y="CLAIM_AMOUNT_PAID")
    plt.title("Average Claim Amount by Month")
    plt.xlabel("Month")
    plt.ylabel("Average Claim Amount (€)")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(2, 2, 3)
    quarter_count = df.groupby("CLAIM_QUARTER")["CLAIM_ID"].count().reset_index()
    sns.barplot(data=quarter_count, x="CLAIM_QUARTER", y="CLAIM_ID")
    plt.title("Number of Claims by Quarter")
    plt.xlabel("Quarter")
    plt.ylabel("Number of Claims")

    plt.subplot(2, 2, 4)
    # Warranty type seasonality (quarterly)
    top_warranties = df["WARRANTY"].value_counts().head(5).index
    warranty_quarter_df = df[df["WARRANTY"].isin(top_warranties)]
    warranty_quarter_counts = pd.crosstab(
        warranty_quarter_df["CLAIM_QUARTER"], warranty_quarter_df["WARRANTY"]
    )

    # Normalize to show percentage by quarter
    warranty_quarter_pct = warranty_quarter_counts.div(
        warranty_quarter_counts.sum(axis=1), axis=0
    )
    sns.heatmap(warranty_quarter_pct, annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title("Warranty Type Distribution by Quarter (Top 5)")
    plt.xlabel("Warranty Type")
    plt.ylabel("Quarter")

    plt.tight_layout()
    plt.savefig("visualizations/temporal_analysis.png")
    print(
        "Saved temporal analysis visualization to visualizations/temporal_analysis.png"
    )

    return monthly_claims, quarterly_claims


def generate_business_insights(df, warranty_analysis, region_analysis):
    """
    Generate business insights from the claims data analysis
    """
    print("\n==== BUSINESS INSIGHTS ====")

    # Loss Ratio Analysis
    high_loss_ratio_warranties = warranty_analysis.sort_values(
        "Avg_Loss_Ratio", ascending=False
    ).head(3)
    high_loss_ratio_regions = region_analysis.sort_values(
        "Avg_Loss_Ratio", ascending=False
    ).head(3)

    print("\n1. High Loss Ratio Products (Warranty Types):")
    print(
        high_loss_ratio_warranties[
            ["Avg_Loss_Ratio", "Claim_Count", "Avg_Claim_Amount", "Avg_Premium"]
        ]
    )

    print("\n2. High Loss Ratio Regions:")
    print(
        high_loss_ratio_regions[
            ["Avg_Loss_Ratio", "Claim_Count", "Avg_Claim_Amount", "Avg_Premium"]
        ]
    )

    # Claim Amount Analysis by Age and Gender
    age_gender_amount = (
        df.groupby(["AGE_GROUP", "POLICYHOLDER_GENDER"])["CLAIM_AMOUNT_PAID"]
        .mean()
        .reset_index()
    )
    high_claim_segments = age_gender_amount.sort_values(
        "CLAIM_AMOUNT_PAID", ascending=False
    ).head(5)

    print("\n3. Highest Average Claim Amount by Age-Gender Segment:")
    print(high_claim_segments)

    # Vehicle Analysis
    risky_vehicles = (
        df.groupby("VEHICLE_BRAND")
        .agg({"CLAIM_ID": "count", "CLAIM_AMOUNT_PAID": "mean", "LOSS_RATIO": "mean"})
        .sort_values("LOSS_RATIO", ascending=False)
        .head(5)
    )

    print("\n4. Riskiest Vehicle Brands (By Loss Ratio):")
    print(risky_vehicles)

    # Seasonal Analysis
    month_amount = df.groupby("CLAIM_MONTH_NAME")["CLAIM_AMOUNT_PAID"].mean()
    high_claim_months = month_amount.sort_values(ascending=False).head(3)

    print("\n5. Months with Highest Average Claim Amounts:")
    print(high_claim_months)

    # Visualize key business insights
    plt.figure(figsize=(16, 14))

    plt.subplot(2, 2, 1)
    warranties = high_loss_ratio_warranties.index.get_level_values("WARRANTY").tolist()
    sns.barplot(x=warranties, y=high_loss_ratio_warranties["Avg_Loss_Ratio"])
    plt.title("Top 3 Warranty Types by Loss Ratio")
    plt.xlabel("Warranty Type")
    plt.ylabel("Average Loss Ratio")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(2, 2, 2)
    regions = high_loss_ratio_regions.index.get_level_values("CLAIM_REGION").tolist()
    sns.barplot(x=regions, y=high_loss_ratio_regions["Avg_Loss_Ratio"])
    plt.title("Top 3 Regions by Loss Ratio")
    plt.xlabel("Region")
    plt.ylabel("Average Loss Ratio")
    plt.xticks(rotation=45, ha="right")

    plt.subplot(2, 2, 3)
    pivot_df = high_claim_segments.pivot(
        index="AGE_GROUP", columns="POLICYHOLDER_GENDER", values="CLAIM_AMOUNT_PAID"
    )
    sns.heatmap(pivot_df, annot=True, cmap="YlOrRd", fmt=".2f")
    plt.title("Average Claim Amount by Age-Gender Segment")
    plt.xlabel("Gender")
    plt.ylabel("Age Group")

    plt.subplot(2, 2, 4)
    sns.barplot(x=risky_vehicles.index, y=risky_vehicles["LOSS_RATIO"])
    plt.title("Top 5 Riskiest Vehicle Brands by Loss Ratio")
    plt.xlabel("Vehicle Brand")
    plt.ylabel("Average Loss Ratio")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig("visualizations/business_insights.png")
    print(
        "Saved business insights visualization to visualizations/business_insights.png"
    )


def export_analysis_to_file(output_text, file_path="insurance_claims_analysis.txt"):
    """
    Export the analysis output to a text file
    """
    with open(file_path, "w") as f:
        f.write("===============================================================\n")
        f.write("                INSURANCE CLAIMS ANALYSIS REPORT                \n")
        f.write("===============================================================\n")
        f.write(
            "\nGenerated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
        )
        f.write(output_text)
        f.write("\n\n===============================================================\n")
        f.write("                      END OF REPORT                            \n")
        f.write("===============================================================\n")

    print(f"\nAnalysis exported to {file_path}")
    return file_path


def main():
    """
    Main function to orchestrate the insurance claims data analysis
    """
    # Capture all output
    with CaptureOutput() as captured:
        # Load dataset
        df = load_data()
        print(f"Loaded {len(df)} insurance claims records")

        # Explore data
        explore_data(df)

        # Analyze claims by warranty type
        warranty_analysis = analyze_claims_by_warranty(df)

        # Analyze claims by demographics
        gender_analysis, age_analysis = analyze_claims_by_demographics(df)

        # Analyze claims by vehicle
        vehicle_analysis = analyze_claims_by_vehicle(df)

        # Analyze claims by geography
        region_analysis = analyze_claims_by_geography(df)

        # Analyze temporal patterns
        monthly_claims, quarterly_claims = analyze_temporal_patterns(df)

        # Generate business insights
        generate_business_insights(df, warranty_analysis, region_analysis)

        print("\n==== ANALYSIS COMPLETE ====")
        print("Check the 'visualizations' directory for generated visualizations")
        print("\nBusiness Consultant Summary:")
        print(
            "1. Analyzed insurance claims data to identify high-risk warranty types and geographical regions"
        )
        print("2. Identified demographic segments with higher claim amounts")
        print("3. Determined vehicle brands with unfavorable loss ratios")
        print("4. Discovered seasonal patterns in claims frequency and severity")
        print(
            "5. Suggested focusing on pricing adjustments for high-loss products and regions"
        )

    # Get the captured output
    analysis_output = captured.get_output()

    # Export the analysis to a text file
    export_file = export_analysis_to_file(analysis_output)

    # Print the original output to console as well
    print(analysis_output)

    return export_file


if __name__ == "__main__":
    main()
