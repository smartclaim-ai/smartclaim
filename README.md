<p align="center">
  <img src="assets/logo.png" width="250" alt="Logo" />
</p>

<h1 align="center">
  SmartClaim: Comprehensive Vehicle Insurance Claims Analysis
</h1>

<p align="center">
  SmartClaim leverages advanced data analytics and AI-driven insights to deliver a comprehensive analysis of vehicle insurance claims data. Its primary goal is to empower insurance companies with actionable intelligence to optimize risk assessment, refine pricing strategies, improve product offerings, and streamline claims operations.
</p>

## Table of Contents

1. [Key Goals](#key-goals)
2. [Dataset Description](#dataset-description)
3. [Methodology](#methodology)
4. [Project Setup](#project-setup)
5. [How to Use](#how-to-use)
6. [Structure of the `analysis` Output Folder](#structure-of-the-analysis-output-folder)

## Key Goals

1.  **Granular Risk Assessment:** To identify high-risk segments across different warranty types, policyholder demographics (age), vehicle characteristics (brand), and geographical locations (region/province).
2.  **Inform Pricing and Underwriting:** Provide data to support more accurate premium setting and risk selection.
3.  **Product Insights:** Understand the claims behavior for different insurance products (warranties) to guide product refinement.
4.  **Operational Efficiency:** Highlight patterns that might inform claims handling processes or fraud detection efforts (though fraud detection is not an explicit output of this script).

## Dataset Description

The analysis is performed on a dataset (`data/data.csv`) containing vehicle insurance claims with the following columns:

-   **CLAIM_ID:** A unique identifier assigned to each claim.
-   **POLICYHOLDER_AGE:** The age of the policyholder.
-   **POLICYHOLDER_GENDER:** The gender of the policyholder.
-   **WARRANTY:** The type of warranty affected by the claim (e.g., Civil Liability, Glasses, Theft).
-   **CLAIM_DATE:** The date the claim was officially recorded with the insurance company.
-   **CLAIM_REGION:** The region where the accident occurred.
-   **CLAIM_PROVINCE:** The province where the accident occurred.
-   **VEHICLE_BRAND:** The brand of the vehicle of the policyholder involved in the claim.
-   **VEHICLE_MODEL:** The model of the vehicle of the policyholder involved in the claim.
-   **CLAIM_AMOUNT_PAID:** The total amount paid by the insurance company to settle the claim.
-   **PREMIUM_AMOUNT_PAID:** The (assumed annual) amount the policyholder pays to the insurance company for coverage.

## Methodology

The analysis is conducted using a Python script (`analyze_data.py`) leveraging the pandas library for data manipulation and matplotlib/seaborn for visualization. The core methodology involves:

1.  **Data Loading and Cleaning:**
    -   Loading the dataset from `data/data.csv`.
    -   Parsing `CLAIM_DATE` strings into datetime objects, specifying the `dd/mm/yyyy` format.
    -   Handling missing values: Categorical fields like `POLICYHOLDER_GENDER`, `CLAIM_REGION`, `CLAIM_PROVINCE`, `VEHICLE_BRAND`, and `VEHICLE_MODEL` have missing values imputed (e.g., with "Unknown" or the mode).
2.  **Descriptive Statistics:** Generating overall descriptive statistics for the cleaned dataset.
3.  **Segmentation and Aggregation:** The data is grouped and analyzed across multiple dimensions:
    -   **Overall Dataset Analysis:** Examining trends across the entire dataset for age, vehicle brand, and geography.
    -   **Civil Liability Deep Dive:** A focused analysis on "CIVIL LIABILITY INSURANCE" claims, segmented by age, vehicle brand, and geography.
    -   **Tiered Coverage Analysis:** Investigating "GLASSES" and "TRAVEL ASSISTANCE" warranties, focusing on premium consistency and claim amount distributions to assess potential for tiered product offerings.
    -   **Other Specific Warranty Analysis:** Iterating through all other unique warranty types in the dataset. For each warranty with a sufficient number of claims (currently >= 30), a detailed breakdown by policyholder age, vehicle brand, and claim region is performed. Warranties below this threshold receive a basic statistical summary.
4.  **Metrics Calculated per Segment:**
    -   **Number of Claims:** To understand claim frequency.
    -   **Average Claim Amount:** To understand claim severity.
    -   **Total Claim Amount Paid & Total Premium for Claiming Policies:** Used in the illustrative loss indication.
5.  **Illustrative Loss Indication:**
    -   An indicative "Payout vs. Annual Premium for Claimers (%)" is calculated for each warranty type. This compares the total claim amounts paid for a warranty to the sum of annual premiums _of those specific policies that made a claim under that warranty_.
    -   **Important Caveat:** This is not a true actuarial loss ratio for the entire portfolio for each warranty, as it doesn't account for premiums from policies that did not claim. It serves as an indicator of payout levels relative to premiums _among claimants_.
6.  **Visualization & Reporting:**
    -   Bar charts and histograms are generated to visually represent the findings (e.g., claims by age group, average claim amounts by vehicle brand).
    -   All generated tables are saved as human-readable `.txt` files, and plots are saved as `.png` images.
    -   Outputs are organized into a structured directory (`analysis/`) with subfolders for each distinct analysis category, facilitating easy navigation and review.

## Project Setup

1.  **Python:** Ensure you have Python 3.8 or newer installed.
2.  **Virtual Environment (Recommended):** It's highly recommended to use a Python virtual environment to manage project dependencies.
    -   Create a virtual environment (e.g., named `venv`):
        ```bash
        python -m venv venv
        ```
    -   Activate the virtual environment:
        -   On macOS and Linux:
            ```bash
            source venv/bin/activate
            ```
        -   On Windows:
            ```bash
            venv\Scripts\activate
            ```
3.  **Install Dependencies:** Once the virtual environment is activated, install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
    _(Ensure `requirements.txt` exists and contains `pandas`, `matplotlib`, and `seaborn`.)_

## How to Use

1.  **Place Data:** Ensure your claims data is available at `data/data.csv`.
2.  **Minimise the Dataset (optional)**: If you want to run the analysis on a smaller dataset, you can use the `data/minimized_data.csv` file or run the `minimize_data.py` script to generate your own.
3.  **Run the Analysis Script:** Execute the main analysis script from your terminal:
    ```bash
    python analyze_data.py
    ```
4.  **Review Outputs:** The script will:
    -   Print progress and key summary tables to the console.
    -   Create an `analysis` directory in your project root if it doesn't exist.
    -   Populate the `analysis` directory with a structured set of subfolders containing:
        -   `.txt` files for all generated data tables.
        -   `.png` files for all generated visualizations.

## Structure of the `analysis` Output Folder

The `analysis` directory will be organized as follows:

-   `main_reports/`: Contains overall descriptive statistics and the illustrative loss indication table for all warranties.
-   `overall_analysis/`:
    -   `age_analysis/`: Overall claims analyzed by policyholder age.
    -   `vehicle_brand_analysis/`: Overall claims analyzed by vehicle brand.
    -   `geographical_analysis/`: Overall claims analyzed by region and province.
-   `civil_liability_analysis/`:
    -   `age_analysis/`: "CIVIL LIABILITY INSURANCE" claims by policyholder age.
    -   `vehicle_brand_analysis/`: "CIVIL LIABILITY INSURANCE" claims by vehicle brand.
    -   `geographical_analysis/`: "CIVIL LIABILITY INSURANCE" claims by region and province.
-   `tiered_coverage_analysis/`: Analysis for "GLASSES" and "TRAVEL ASSISTANCE" (premium & claim distributions).
-   `other_warranties_analysis/`:
    -   Contains a subfolder for each other significant warranty type (e.g., `VEHICLE_FIRE/`, `THEFT/`).
    -   Each subfolder includes analyses by age, vehicle brand, and region for that specific warranty.

By systematically analyzing the claims data, this project aims to empower the insurance company to optimize its portfolio, manage risk more effectively, and improve overall profitability.
