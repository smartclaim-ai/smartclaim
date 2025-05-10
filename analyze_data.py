import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re  # For sanitizing filenames


# --- Helper function to sanitize string for filenames/directory names ---
def sanitize_filename(name):
    # Remove special characters, replace spaces with underscores
    name = re.sub(r"[^a-zA-Z0-9_\s-]", "", name)
    name = re.sub(r"[\s/]", "_", name)
    return name


# --- Helper function to save DataFrame to .txt file ---
def save_df_to_txt(df, filename, header=""):
    # Ensure the directory for the filename exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        if header:
            f.write(header + "\n\n")
        f.write(df.to_string())
    print(f"Saved table: {filename}")


# --- Helper function to save plot ---
def save_plot(plt_figure, filename):
    # Ensure the directory for the filename exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt_figure.savefig(filename)
    print(f"Saved plot: {filename}")
    plt.close(plt_figure)  # Close the figure to free memory


# --- Output Directory Setup ---
base_output_dir = "analysis"
main_reports_dir = os.path.join(base_output_dir, "main_reports")
cl_output_dir = os.path.join(base_output_dir, "civil_liability_analysis")
cl_age_dir = os.path.join(cl_output_dir, "age_analysis")
cl_brand_dir = os.path.join(cl_output_dir, "vehicle_brand_analysis")
cl_geo_dir = os.path.join(cl_output_dir, "geographical_analysis")
tiered_output_dir = os.path.join(base_output_dir, "tiered_coverage_analysis")
other_warranties_main_dir = os.path.join(base_output_dir, "other_warranties_analysis")
overall_output_dir = os.path.join(base_output_dir, "overall_analysis")
overall_age_dir = os.path.join(overall_output_dir, "age_analysis")
overall_brand_dir = os.path.join(overall_output_dir, "vehicle_brand_analysis")
overall_geo_dir = os.path.join(overall_output_dir, "geographical_analysis")

for path_dir in [
    base_output_dir,
    main_reports_dir,
    cl_output_dir,
    cl_age_dir,
    cl_brand_dir,
    cl_geo_dir,
    tiered_output_dir,
    other_warranties_main_dir,
    overall_output_dir,
    overall_age_dir,
    overall_brand_dir,
    overall_geo_dir,
]:
    os.makedirs(path_dir, exist_ok=True)
print(f"Base output directory structure created under '{base_output_dir}'.")

# Minimum number of claims for a warranty to undergo detailed analysis
MIN_CLAIMS_FOR_DETAILED_WARRANTY_ANALYSIS = 30
TOP_N_DEFAULT = 15  # Default for Top N listings in plots/tables

# Load the dataset
try:
    df = pd.read_csv("data/data.csv")

    # --- Initial Data Cleaning and Preparation ---
    print("\n--- Initial Data Cleaning and Preparation ---")
    print(f"Initial number of rows: {len(df)}")
    original_claim_dates = df["CLAIM_DATE"].copy()
    df["CLAIM_DATE"] = pd.to_datetime(
        df["CLAIM_DATE"], format="%d/%m/%Y", errors="coerce"
    )
    invalid_date_rows = df[df["CLAIM_DATE"].isna()]
    if not invalid_date_rows.empty:
        print(
            f"\nFound {len(invalid_date_rows)} rows with invalid CLAIM_DATE format..."
        )
        # print(original_claim_dates[invalid_date_rows.index].head()) # Keep console less verbose
    else:
        print("\nNo invalid CLAIM_DATE formats found during conversion.")

    df["POLICYHOLDER_GENDER"].fillna(
        (
            df["POLICYHOLDER_GENDER"].mode()[0]
            if not df["POLICYHOLDER_GENDER"].mode().empty
            else "Unknown"
        ),
        inplace=True,
    )
    for col in ["CLAIM_REGION", "CLAIM_PROVINCE", "VEHICLE_BRAND", "VEHICLE_MODEL"]:
        df[col].fillna("Unknown", inplace=True)
    df.dropna(subset=["CLAIM_DATE"], inplace=True)
    print(f"Number of rows after initial cleaning: {len(df)}")

    df.info()
    descriptive_stats = df.describe(include="all")
    print("\nDescriptive Statistics (also saved to .txt):")
    print(descriptive_stats)
    save_df_to_txt(
        descriptive_stats, os.path.join(main_reports_dir, "descriptive_statistics.txt")
    )
    print("\n---------------------------------------\n")

    # --- Analysis for "Granular Risk Assessment for Civil Liability" ---
    print("--- Analyzing Data for Civil Liability Insurance ---")
    civil_liability_df = df[df["WARRANTY"] == "CIVIL LIABILITY INSURANCE"].copy()

    if not civil_liability_df.empty:
        print(f"Found {len(civil_liability_df)} claims for CIVIL LIABILITY INSURANCE.")

        # Age Analysis
        print("\n--- CL: Age Analysis ---")
        age_bins = [18, 25, 35, 45, 55, 65, 130]
        age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
        civil_liability_df.loc[:, "AGE_GROUP"] = pd.cut(
            civil_liability_df["POLICYHOLDER_AGE"],
            bins=age_bins,
            labels=age_labels,
            right=False,
        )

        age_group_claims_cl = (
            civil_liability_df.groupby("AGE_GROUP", observed=False)["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
        )
        save_df_to_txt(
            age_group_claims_cl,
            os.path.join(cl_age_dir, "cl_claims_by_age_group.txt"),
            "Number of Civil Liability Claims by Age Group",
        )
        fig1 = plt.figure(figsize=(10, 6))
        sns.barplot(
            x="AGE_GROUP",
            y="NUMBER_OF_CLAIMS",
            data=age_group_claims_cl,
            palette="viridis",
            ax=fig1.gca(),
        )
        fig1.gca().set_title("Number of Civil Liability Claims by Age Group")
        plt.tight_layout()
        save_plot(fig1, os.path.join(cl_age_dir, "cl_claims_by_age_group.png"))

        age_group_avg_amount_cl = (
            civil_liability_df.groupby("AGE_GROUP", observed=False)["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
        )
        save_df_to_txt(
            age_group_avg_amount_cl,
            os.path.join(cl_age_dir, "cl_avg_amount_by_age_group.txt"),
            "Average Civil Liability Claim Amount by Age Group",
        )
        fig2 = plt.figure(figsize=(10, 6))
        sns.barplot(
            x="AGE_GROUP",
            y="AVERAGE_CLAIM_AMOUNT",
            data=age_group_avg_amount_cl,
            palette="mako",
            ax=fig2.gca(),
        )
        fig2.gca().set_title("Average Civil Liability Claim Amount by Age Group")
        plt.tight_layout()
        save_plot(fig2, os.path.join(cl_age_dir, "cl_avg_amount_by_age_group.png"))

        # Vehicle Brand Analysis
        print("\n--- CL: Vehicle Brand Analysis ---")
        brand_claim_counts_cl = (
            civil_liability_df.groupby("VEHICLE_BRAND")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        save_df_to_txt(
            brand_claim_counts_cl,
            os.path.join(cl_brand_dir, "cl_claims_by_brand.txt"),
            f"Civil Liability Claims by Vehicle Brand (Top {TOP_N_DEFAULT} shown in plot)",
        )
        fig3 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="NUMBER_OF_CLAIMS",
            y="VEHICLE_BRAND",
            data=brand_claim_counts_cl.head(TOP_N_DEFAULT),
            palette="viridis_r",
            orient="h",
            ax=fig3.gca(),
        )
        fig3.gca().set_title(
            f"Top {TOP_N_DEFAULT} Vehicle Brands by Number of CL Claims"
        )
        plt.tight_layout()
        save_plot(fig3, os.path.join(cl_brand_dir, "cl_num_claims_by_brand.png"))

        brand_avg_amount_cl = (
            civil_liability_df.groupby("VEHICLE_BRAND")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        save_df_to_txt(
            brand_avg_amount_cl,
            os.path.join(cl_brand_dir, "cl_avg_amount_by_brand.txt"),
            f"Avg Civil Liability Claim Amount by Vehicle Brand (Top {TOP_N_DEFAULT} shown in plot)",
        )
        fig4 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="AVERAGE_CLAIM_AMOUNT",
            y="VEHICLE_BRAND",
            data=brand_avg_amount_cl.head(TOP_N_DEFAULT),
            palette="rocket",
            orient="h",
            ax=fig4.gca(),
        )
        fig4.gca().set_title(
            f"Top {TOP_N_DEFAULT} Vehicle Brands by Avg CL Claim Amount"
        )
        plt.tight_layout()
        save_plot(fig4, os.path.join(cl_brand_dir, "cl_avg_amount_by_brand.png"))

        # Geographical Analysis (Region & Province)
        print("\n--- CL: Geographical Analysis ---")
        region_claim_counts_cl = (
            civil_liability_df.groupby("CLAIM_REGION")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        save_df_to_txt(
            region_claim_counts_cl,
            os.path.join(cl_geo_dir, "cl_claims_by_region.txt"),
            "CL Claims by Region",
        )
        fig5 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="NUMBER_OF_CLAIMS",
            y="CLAIM_REGION",
            data=region_claim_counts_cl,
            palette="magma",
            orient="h",
            ax=fig5.gca(),
        )
        fig5.gca().set_title("Number of CL Claims by Claim Region")
        plt.tight_layout()
        save_plot(fig5, os.path.join(cl_geo_dir, "cl_num_claims_by_region.png"))

        region_avg_amount_cl = (
            civil_liability_df.groupby("CLAIM_REGION")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        save_df_to_txt(
            region_avg_amount_cl,
            os.path.join(cl_geo_dir, "cl_avg_amount_by_region.txt"),
            "Avg CL Claim Amount by Region",
        )
        fig6 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="AVERAGE_CLAIM_AMOUNT",
            y="CLAIM_REGION",
            data=region_avg_amount_cl,
            palette="cubehelix",
            orient="h",
            ax=fig6.gca(),
        )
        fig6.gca().set_title("Average CL Claim Amount by Claim Region")
        plt.tight_layout()
        save_plot(fig6, os.path.join(cl_geo_dir, "cl_avg_amount_by_region.png"))

        province_claim_counts_cl = (
            civil_liability_df.groupby("CLAIM_PROVINCE")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        save_df_to_txt(
            province_claim_counts_cl,
            os.path.join(cl_geo_dir, "cl_claims_by_province.txt"),
            f"CL Claims by Province (Top {TOP_N_DEFAULT} shown in plot)",
        )
        fig7 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="NUMBER_OF_CLAIMS",
            y="CLAIM_PROVINCE",
            data=province_claim_counts_cl.head(TOP_N_DEFAULT),
            palette="plasma",
            orient="h",
            ax=fig7.gca(),
        )
        fig7.gca().set_title(f"Top {TOP_N_DEFAULT} Provinces by Number of CL Claims")
        plt.tight_layout()
        save_plot(fig7, os.path.join(cl_geo_dir, "cl_num_claims_by_province.png"))

        province_avg_amount_cl = (
            civil_liability_df.groupby("CLAIM_PROVINCE")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        save_df_to_txt(
            province_avg_amount_cl,
            os.path.join(cl_geo_dir, "cl_avg_amount_by_province.txt"),
            f"Avg CL Claim Amount by Province (Top {TOP_N_DEFAULT} in plot)",
        )
        fig8 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="AVERAGE_CLAIM_AMOUNT",
            y="CLAIM_PROVINCE",
            data=province_avg_amount_cl.head(TOP_N_DEFAULT),
            palette="crest",
            orient="h",
            ax=fig8.gca(),
        )
        fig8.gca().set_title(f"Top {TOP_N_DEFAULT} Provinces by Avg CL Claim Amount")
        plt.tight_layout()
        save_plot(fig8, os.path.join(cl_geo_dir, "cl_avg_amount_by_province.png"))
    else:
        print("No data for CIVIL LIABILITY INSURANCE. Skipping CL analysis.")

    # --- Analysis for Tiered Coverage (Glasses & Travel Assistance) ---
    print(
        "\n\n--- Analyzing Data for Tiered Coverage (Glasses & Travel Assistance) ---"
    )
    tiered_warranties = ["GLASSES", "TRAVEL ASSISTANCE"]
    tiered_warranty_df = df[df["WARRANTY"].isin(tiered_warranties)].copy()

    if not tiered_warranty_df.empty:
        premium_dist_tiered = (
            tiered_warranty_df.groupby("WARRANTY")["PREMIUM_AMOUNT_PAID"]
            .agg(["mean", "min", "max", "nunique", "count"])
            .reset_index()
        )
        save_df_to_txt(
            premium_dist_tiered,
            os.path.join(tiered_output_dir, "premium_distribution.txt"),
            "Premium Amount Distribution for Glasses & Travel Assistance",
        )

        claim_dist_tiered = (
            tiered_warranty_df.groupby("WARRANTY")["CLAIM_AMOUNT_PAID"]
            .agg(["mean", "median", "min", "max", "std"])
            .reset_index()
        )
        save_df_to_txt(
            claim_dist_tiered,
            os.path.join(tiered_output_dir, "claim_distribution.txt"),
            "Claim Amount Distribution for Glasses & Travel Assistance",
        )

        for warranty_name in tiered_warranties:
            warranty_data = tiered_warranty_df[
                tiered_warranty_df["WARRANTY"] == warranty_name
            ]
            if not warranty_data.empty:
                fig_hist = plt.figure(figsize=(10, 6))
                sns.histplot(
                    warranty_data["CLAIM_AMOUNT_PAID"],
                    kde=True,
                    bins=30,
                    ax=fig_hist.gca(),
                )
                fig_hist.gca().set_title(
                    f"Distribution of Claim Amounts for {warranty_name}"
                )
                plt.tight_layout()
                save_plot(
                    fig_hist,
                    os.path.join(
                        tiered_output_dir,
                        f"{sanitize_filename(warranty_name)}_claim_dist.png",
                    ),
                )
    else:
        print(
            "No data for GLASSES or TRAVEL ASSISTANCE. Skipping tiered coverage analysis."
        )

    # --- General Loss Ratio Analysis (Illustrative) ---
    print("\n\n--- Illustrative Loss Indication (All Warranties) ---")
    warranty_summary = (
        df.groupby("WARRANTY")
        .agg(
            TOTAL_CLAIM_AMOUNT_PAID=("CLAIM_AMOUNT_PAID", "sum"),
            TOTAL_PREMIUM_FOR_CLAIMING_POLICIES=("PREMIUM_AMOUNT_PAID", "sum"),
            NUMBER_OF_CLAIMS=("CLAIM_ID", "count"),
            AVERAGE_PREMIUM_FOR_CLAIMING_POLICIES=("PREMIUM_AMOUNT_PAID", "mean"),
            AVERAGE_CLAIM_COST=(
                "CLAIM_AMOUNT_PAID",
                "mean",
            ),  # Changed from calculating later
        )
        .reset_index()
    )
    warranty_summary["INDICATIVE_PAYOUT_VS_ANNUAL_PREMIUM_FOR_CLAIMERS (%)"] = (
        warranty_summary["TOTAL_CLAIM_AMOUNT_PAID"]
        / warranty_summary["TOTAL_PREMIUM_FOR_CLAIMING_POLICIES"].replace(0, pd.NA)
    ) * 100  # Avoid div by zero

    warranty_summary_output = warranty_summary[
        [
            "WARRANTY",
            "NUMBER_OF_CLAIMS",
            "AVERAGE_PREMIUM_FOR_CLAIMING_POLICIES",
            "AVERAGE_CLAIM_COST",
            "TOTAL_CLAIM_AMOUNT_PAID",
            "TOTAL_PREMIUM_FOR_CLAIMING_POLICIES",
            "INDICATIVE_PAYOUT_VS_ANNUAL_PREMIUM_FOR_CLAIMERS (%)",
        ]
    ].sort_values(
        by="INDICATIVE_PAYOUT_VS_ANNUAL_PREMIUM_FOR_CLAIMERS (%)", ascending=False
    )
    save_df_to_txt(
        warranty_summary_output,
        os.path.join(main_reports_dir, "illustrative_loss_indication_by_warranty.txt"),
        "Indicative Payout vs. Annual Premium (Claiming Policies)",
    )

    # --- Analysis of Other Warranty Types ---
    print("\n\n--- Analyzing Other Specific Warranty Types ---")
    all_warranty_types = df["WARRANTY"].unique()
    analyzed_main = ["CIVIL LIABILITY INSURANCE", "GLASSES", "TRAVEL ASSISTANCE"]

    for warranty_name in all_warranty_types:
        if warranty_name in analyzed_main:
            continue

        print(f"\n-- Analyzing Warranty: {warranty_name} --")
        warranty_df = df[df["WARRANTY"] == warranty_name].copy()
        num_claims = len(warranty_df)
        print(f"Found {num_claims} claims for {warranty_name}.")

        if num_claims < MIN_CLAIMS_FOR_DETAILED_WARRANTY_ANALYSIS:
            print(
                f"Skipping detailed analysis for {warranty_name} due to insufficient claims (less than {MIN_CLAIMS_FOR_DETAILED_WARRANTY_ANALYSIS})."
            )
            # Save a simple summary if desired, or just skip
            simple_summary = warranty_df[
                ["CLAIM_AMOUNT_PAID", "PREMIUM_AMOUNT_PAID"]
            ].describe()
            current_warranty_dir = os.path.join(
                other_warranties_main_dir, sanitize_filename(warranty_name)
            )
            save_df_to_txt(
                simple_summary,
                os.path.join(current_warranty_dir, "basic_stats_summary.txt"),
                f"Basic Stats for {warranty_name} ({num_claims} claims)",
            )
            continue

        current_warranty_dir = os.path.join(
            other_warranties_main_dir, sanitize_filename(warranty_name)
        )
        os.makedirs(current_warranty_dir, exist_ok=True)

        # Age Analysis for this warranty
        warranty_df.loc[:, "AGE_GROUP"] = pd.cut(
            warranty_df["POLICYHOLDER_AGE"],
            bins=age_bins,
            labels=age_labels,
            right=False,
        )
        age_claims_other = (
            warranty_df.groupby("AGE_GROUP", observed=False)["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
        )
        if not age_claims_other.empty:
            save_df_to_txt(
                age_claims_other,
                os.path.join(current_warranty_dir, "claims_by_age_group.txt"),
                f"Claims by Age Group for {warranty_name}",
            )
            fig_age_c = plt.figure(figsize=(10, 6))
            sns.barplot(
                x="AGE_GROUP",
                y="NUMBER_OF_CLAIMS",
                data=age_claims_other,
                palette="coolwarm",
                ax=fig_age_c.gca(),
            ).set_title(f"Claims by Age Group - {warranty_name}")
            plt.tight_layout()
            save_plot(
                fig_age_c, os.path.join(current_warranty_dir, "claims_by_age_group.png")
            )

        age_avg_amount_other = (
            warranty_df.groupby("AGE_GROUP", observed=False)["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
        )
        if not age_avg_amount_other.empty:
            save_df_to_txt(
                age_avg_amount_other,
                os.path.join(current_warranty_dir, "avg_amount_by_age_group.txt"),
                f"Avg Claim Amount by Age Group for {warranty_name}",
            )
            fig_age_a = plt.figure(figsize=(10, 6))
            sns.barplot(
                x="AGE_GROUP",
                y="AVERAGE_CLAIM_AMOUNT",
                data=age_avg_amount_other,
                palette="summer",
                ax=fig_age_a.gca(),
            ).set_title(f"Avg Claim Amount by Age Group - {warranty_name}")
            plt.tight_layout()
            save_plot(
                fig_age_a,
                os.path.join(current_warranty_dir, "avg_amount_by_age_group.png"),
            )

        # Vehicle Brand Analysis for this warranty
        brand_claims_other = (
            warranty_df.groupby("VEHICLE_BRAND")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        if not brand_claims_other.empty:
            save_df_to_txt(
                brand_claims_other,
                os.path.join(current_warranty_dir, "claims_by_brand.txt"),
                f"Claims by Brand for {warranty_name} (Top {TOP_N_DEFAULT} in plot)",
            )
            fig_brand_c = plt.figure(figsize=(12, 8))
            sns.barplot(
                x="NUMBER_OF_CLAIMS",
                y="VEHICLE_BRAND",
                data=brand_claims_other.head(TOP_N_DEFAULT),
                palette="winter_r",
                orient="h",
                ax=fig_brand_c.gca(),
            ).set_title(f"Top {TOP_N_DEFAULT} Brands by Claims - {warranty_name}")
            plt.tight_layout()
            save_plot(
                fig_brand_c, os.path.join(current_warranty_dir, "claims_by_brand.png")
            )

        brand_avg_amount_other = (
            warranty_df.groupby("VEHICLE_BRAND")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        if not brand_avg_amount_other.empty:
            save_df_to_txt(
                brand_avg_amount_other,
                os.path.join(current_warranty_dir, "avg_amount_by_brand.txt"),
                f"Avg Claim Amount by Brand for {warranty_name} (Top {TOP_N_DEFAULT} in plot)",
            )
            fig_brand_a = plt.figure(figsize=(12, 8))
            sns.barplot(
                x="AVERAGE_CLAIM_AMOUNT",
                y="VEHICLE_BRAND",
                data=brand_avg_amount_other.head(TOP_N_DEFAULT),
                palette="spring_r",
                orient="h",
                ax=fig_brand_a.gca(),
            ).set_title(f"Top {TOP_N_DEFAULT} Brands by Avg Amount - {warranty_name}")
            plt.tight_layout()
            save_plot(
                fig_brand_a,
                os.path.join(current_warranty_dir, "avg_amount_by_brand.png"),
            )

        # Region Analysis for this warranty
        region_claims_other = (
            warranty_df.groupby("CLAIM_REGION")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        if not region_claims_other.empty:
            save_df_to_txt(
                region_claims_other,
                os.path.join(current_warranty_dir, "claims_by_region.txt"),
                f"Claims by Region for {warranty_name} (Top {TOP_N_DEFAULT} in plot)",
            )
            fig_reg_c = plt.figure(figsize=(12, 8))
            sns.barplot(
                x="NUMBER_OF_CLAIMS",
                y="CLAIM_REGION",
                data=region_claims_other.head(TOP_N_DEFAULT),
                palette="autumn_r",
                orient="h",
                ax=fig_reg_c.gca(),
            ).set_title(f"Top {TOP_N_DEFAULT} Regions by Claims - {warranty_name}")
            plt.tight_layout()
            save_plot(
                fig_reg_c, os.path.join(current_warranty_dir, "claims_by_region.png")
            )

        region_avg_amount_other = (
            warranty_df.groupby("CLAIM_REGION")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        if not region_avg_amount_other.empty:
            save_df_to_txt(
                region_avg_amount_other,
                os.path.join(current_warranty_dir, "avg_amount_by_region.txt"),
                f"Avg Claim Amount by Region for {warranty_name} (Top {TOP_N_DEFAULT} in plot)",
            )
            fig_reg_a = plt.figure(figsize=(12, 8))
            sns.barplot(
                x="AVERAGE_CLAIM_AMOUNT",
                y="CLAIM_REGION",
                data=region_avg_amount_other.head(TOP_N_DEFAULT),
                palette="copper_r",
                orient="h",
                ax=fig_reg_a.gca(),
            ).set_title(f"Top {TOP_N_DEFAULT} Regions by Avg Amount - {warranty_name}")
            plt.tight_layout()
            save_plot(
                fig_reg_a,
                os.path.join(current_warranty_dir, "avg_amount_by_region.png"),
            )

    # --- Analysis for "Granular Risk Assessment for Overall Dataset" ---
    print("--- Analyzing Data for Overall Dataset ---")
    overall_df = df.copy()

    if not overall_df.empty:
        print(f"Found {len(overall_df)} claims for Overall Dataset.")

        # Age Analysis
        print("\n--- Overall Dataset: Age Analysis ---")
        age_bins = [18, 25, 35, 45, 55, 65, 130]
        age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
        overall_df.loc[:, "AGE_GROUP"] = pd.cut(
            overall_df["POLICYHOLDER_AGE"],
            bins=age_bins,
            labels=age_labels,
            right=False,
        )

        age_group_claims_overall = (
            overall_df.groupby("AGE_GROUP", observed=False)["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
        )
        save_df_to_txt(
            age_group_claims_overall,
            os.path.join(overall_age_dir, "overall_claims_by_age_group.txt"),
            "Number of Overall Claims by Age Group",
        )
        fig1 = plt.figure(figsize=(10, 6))
        sns.barplot(
            x="AGE_GROUP",
            y="NUMBER_OF_CLAIMS",
            data=age_group_claims_overall,
            palette="viridis",
            ax=fig1.gca(),
        )
        fig1.gca().set_title("Number of Overall Claims by Age Group")
        plt.tight_layout()
        save_plot(
            fig1, os.path.join(overall_age_dir, "overall_claims_by_age_group.png")
        )

        age_group_avg_amount_overall = (
            overall_df.groupby("AGE_GROUP", observed=False)["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
        )
        save_df_to_txt(
            age_group_avg_amount_overall,
            os.path.join(overall_age_dir, "overall_avg_amount_by_age_group.txt"),
            "Average Overall Claim Amount by Age Group",
        )
        fig2 = plt.figure(figsize=(10, 6))
        sns.barplot(
            x="AGE_GROUP",
            y="AVERAGE_CLAIM_AMOUNT",
            data=age_group_avg_amount_overall,
            palette="mako",
            ax=fig2.gca(),
        )
        fig2.gca().set_title("Average Overall Claim Amount by Age Group")
        plt.tight_layout()
        save_plot(
            fig2, os.path.join(overall_age_dir, "overall_avg_amount_by_age_group.png")
        )

        # Vehicle Brand Analysis
        print("\n--- Overall Dataset: Vehicle Brand Analysis ---")
        brand_claim_counts_overall = (
            overall_df.groupby("VEHICLE_BRAND")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        save_df_to_txt(
            brand_claim_counts_overall,
            os.path.join(overall_brand_dir, "overall_claims_by_brand.txt"),
            f"Overall Claims by Vehicle Brand (Top {TOP_N_DEFAULT} shown in plot)",
        )
        fig3 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="NUMBER_OF_CLAIMS",
            y="VEHICLE_BRAND",
            data=brand_claim_counts_overall.head(TOP_N_DEFAULT),
            palette="viridis_r",
            orient="h",
            ax=fig3.gca(),
        )
        fig3.gca().set_title(
            f"Top {TOP_N_DEFAULT} Vehicle Brands by Number of Overall Claims"
        )
        plt.tight_layout()
        save_plot(
            fig3,
            os.path.join(overall_brand_dir, "overall_num_claims_by_brand.png"),
        )

        brand_avg_amount_overall = (
            overall_df.groupby("VEHICLE_BRAND")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        save_df_to_txt(
            brand_avg_amount_overall,
            os.path.join(overall_brand_dir, "overall_avg_amount_by_brand.txt"),
            f"Avg Overall Claim Amount by Vehicle Brand (Top {TOP_N_DEFAULT} shown in plot)",
        )
        fig4 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="AVERAGE_CLAIM_AMOUNT",
            y="VEHICLE_BRAND",
            data=brand_avg_amount_overall.head(TOP_N_DEFAULT),
            palette="rocket",
            orient="h",
            ax=fig4.gca(),
        )
        fig4.gca().set_title(
            f"Top {TOP_N_DEFAULT} Vehicle Brands by Avg Overall Claim Amount"
        )
        plt.tight_layout()
        save_plot(
            fig4,
            os.path.join(overall_brand_dir, "overall_avg_amount_by_brand.png"),
        )

        # Geographical Analysis (Region & Province)
        print("\n--- Overall Dataset: Geographical Analysis ---")
        region_claim_counts_overall = (
            overall_df.groupby("CLAIM_REGION")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        save_df_to_txt(
            region_claim_counts_overall,
            os.path.join(overall_geo_dir, "overall_claims_by_region.txt"),
            "Overall Claims by Region",
        )
        fig5 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="NUMBER_OF_CLAIMS",
            y="CLAIM_REGION",
            data=region_claim_counts_overall,
            palette="magma",
            orient="h",
            ax=fig5.gca(),
        )
        fig5.gca().set_title("Number of Overall Claims by Claim Region")
        plt.tight_layout()
        save_plot(
            fig5, os.path.join(overall_geo_dir, "overall_num_claims_by_region.png")
        )

        region_avg_amount_overall = (
            overall_df.groupby("CLAIM_REGION")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        save_df_to_txt(
            region_avg_amount_overall,
            os.path.join(overall_geo_dir, "overall_avg_amount_by_region.txt"),
            "Avg Overall Claim Amount by Region",
        )
        fig6 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="AVERAGE_CLAIM_AMOUNT",
            y="CLAIM_REGION",
            data=region_avg_amount_overall,
            palette="cubehelix",
            orient="h",
            ax=fig6.gca(),
        )
        fig6.gca().set_title("Average Overall Claim Amount by Claim Region")
        plt.tight_layout()
        save_plot(
            fig6, os.path.join(overall_geo_dir, "overall_avg_amount_by_region.png")
        )

        province_claim_counts_overall = (
            overall_df.groupby("CLAIM_PROVINCE")["CLAIM_ID"]
            .count()
            .reset_index(name="NUMBER_OF_CLAIMS")
            .sort_values(by="NUMBER_OF_CLAIMS", ascending=False)
        )
        save_df_to_txt(
            province_claim_counts_overall,
            os.path.join(overall_geo_dir, "overall_claims_by_province.txt"),
            f"Overall Claims by Province (Top {TOP_N_DEFAULT} shown in plot)",
        )
        fig7 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="NUMBER_OF_CLAIMS",
            y="CLAIM_PROVINCE",
            data=province_claim_counts_overall.head(TOP_N_DEFAULT),
            palette="plasma",
            orient="h",
            ax=fig7.gca(),
        )
        fig7.gca().set_title(
            f"Top {TOP_N_DEFAULT} Provinces by Number of Overall Claims"
        )
        plt.tight_layout()
        save_plot(
            fig7, os.path.join(overall_geo_dir, "overall_num_claims_by_province.png")
        )

        province_avg_amount_overall = (
            overall_df.groupby("CLAIM_PROVINCE")["CLAIM_AMOUNT_PAID"]
            .mean()
            .reset_index(name="AVERAGE_CLAIM_AMOUNT")
            .sort_values(by="AVERAGE_CLAIM_AMOUNT", ascending=False)
        )
        save_df_to_txt(
            province_avg_amount_overall,
            os.path.join(overall_geo_dir, "overall_avg_amount_by_province.txt"),
            f"Avg Overall Claim Amount by Province (Top {TOP_N_DEFAULT} in plot)",
        )
        fig8 = plt.figure(figsize=(12, 8))
        sns.barplot(
            x="AVERAGE_CLAIM_AMOUNT",
            y="CLAIM_PROVINCE",
            data=province_avg_amount_overall.head(TOP_N_DEFAULT),
            palette="crest",
            orient="h",
            ax=fig8.gca(),
        )
        fig8.gca().set_title(
            f"Top {TOP_N_DEFAULT} Provinces by Avg Overall Claim Amount"
        )
        plt.tight_layout()
        save_plot(
            fig8, os.path.join(overall_geo_dir, "overall_avg_amount_by_province.png")
        )
    else:
        print("No data for Overall Dataset. Skipping Overall analysis.")

    print(
        "\nScript finished successfully. All outputs saved to structured subdirectories in 'analysis' directory."
    )

except FileNotFoundError:
    print(f"Error: 'data/data.csv' not found. Make sure the file path is correct.")
except Exception as e:
    print(f"An error occurred during analysis: {e}")
    import traceback

    traceback.print_exc()
