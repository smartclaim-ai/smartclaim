# Insurance Vehicle Claims Analysis

This project provides comprehensive analysis of vehicle insurance claims data to identify risk patterns and business opportunities.

## Project Overview

As a business consultant for an insurance company, this analysis aims to:

1. Identify high-risk warranty types and geographical regions
2. Analyze demographic patterns in claims
3. Determine vehicle brands with unfavorable loss ratios
4. Discover seasonal patterns in claims frequency and severity
5. Provide actionable business insights for pricing and risk management

## Dataset Description

The dataset contains vehicle insurance claims with the following columns:

-   CLAIM_ID: A unique identifier for each claim
-   POLICYHOLDER_AGE: The age of the policyholder
-   POLICYHOLDER_GENDER: The gender of the policyholder
-   WARRANTY: The type of warranty affected by the claim
-   CLAIM_DATE: The date the claim was officially recorded
-   CLAIM_REGION: The region where the accident occurred
-   CLAIM_PROVINCE: The province where the accident occurred
-   VEHICLE_BRAND: The brand of the vehicle involved in the claim
-   VEHICLE_MODEL: The model of the vehicle involved in the claim
-   CLAIM_AMOUNT_PAID: The total amount paid by the insurance company to settle the claim
-   PREMIUM_AMOUNT_PAID: The amount the policyholder pays to the insurance company for coverage

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

```bash
python analyze_insurance_claims.py
```

This script will:

1. Load the insurance claims data from `data/minimized_data.csv`
2. Explore the data structure and basic statistics
3. Perform multiple analyses across different dimensions:
    - Analysis by warranty type
    - Analysis by demographics (age and gender)
    - Analysis by vehicle characteristics
    - Analysis by geographical location
    - Analysis of temporal patterns
4. Generate business insights and recommendations
5. Create visualizations in the `visualizations` directory

## Analysis Dimensions

### Warranty Analysis

-   Distribution of claims by warranty type
-   Average and median claim amounts by warranty type
-   Loss ratio analysis (claim amount / premium amount)

### Demographic Analysis

-   Claims patterns by policyholder age and gender
-   Identification of high-risk demographic segments

### Vehicle Analysis

-   Top vehicle brands and models by claim frequency
-   Vehicle brands with the highest average claim amounts
-   Correlation between vehicle brands and warranty types

### Geographic Analysis

-   Regional distribution of claims
-   Areas with above-average claim amounts
-   Loss ratio analysis by region

### Temporal Analysis

-   Seasonal patterns in claims frequency
-   Monthly and quarterly trends
-   Warranty type seasonality

## Business Insights

The analysis generates specific business insights including:

-   High loss ratio warranty types requiring pricing adjustments
-   Demographic segments with unfavorable claims experience
-   Vehicle brands associated with higher risk
-   Geographical areas with concentration of risk
-   Seasonal patterns requiring attention
