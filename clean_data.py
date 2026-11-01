"""
Data Cleaning and Dual-View Generation Script
=============================================
Cleans raw Amazon Bestsellers dataset (2009-2019) from Kaggle.
Maintains two explicit views:
  1. All Listings (550 records for historical trends, year-over-year pricing, category splits)
  2. Unique Titles (deduplicated titles for rankings, author leaderboards, distributions)
Exports compact, pre-structured JSON to site/data.json for client-side instant exploration.
"""

import os
import json
import pandas as pd


def clean_bestsellers_data(raw_csv_path="data/raw_bestsellers.csv"):
    print(f"Loading raw data from {raw_csv_path}...")
    df = pd.read_csv(raw_csv_path)

    # -------------------------------------------------------------
    # Cleaning Step 1: Whitespace and Basic String Standardization
    # -------------------------------------------------------------
    for col in ["Name", "Author", "Genre"]:
        df[col] = df[col].astype(str).str.strip()

    # -------------------------------------------------------------
    # Cleaning Step 2: Author Name Standardization
    # Resolve punctuation and spacing discrepancies across years
    # -------------------------------------------------------------
    author_replacements = {
        "George R.R. Martin": "George R. R. Martin",
        "J.K. Rowling": "J. K. Rowling",
    }
    df["Author"] = df["Author"].replace(author_replacements)

    # -------------------------------------------------------------
    # Cleaning Step 3: Title Harmonization
    # Fix casing variations and minor edition subtitle inconsistencies
    # -------------------------------------------------------------
    title_replacements = {
        "The 5 Love Languages: The Secret to Love that Lasts": "The 5 Love Languages: The Secret to Love That Lasts",
        "Eclipse (Twilight Sagas)": "Eclipse (Twilight)",
        "The Girl Who Played with Fire (Millennium)": "The Girl Who Played with Fire (Millennium Series)",
        "The Hunger Games (Book 1)": "The Hunger Games",
    }
    df["Name"] = df["Name"].replace(title_replacements)

    # Ensure correct data types
    df["User Rating"] = pd.to_numeric(df["User Rating"], errors="coerce")
    df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").astype(int)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").astype(float)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype(int)

    # -------------------------------------------------------------
    # View 1: All Listings (Historical Time-Series View)
    # -------------------------------------------------------------
    all_listings_path = "data/cleaned_all_listings.csv"
    df.to_csv(all_listings_path, index=False)
    print(f"Saved View 1 (All Listings): {all_listings_path} ({len(df)} rows)")

    # -------------------------------------------------------------
    # View 2: Unique Titles (Rankings & Distribution View)
    # Deduplicate by Name & Author, retaining the listing with peak reviews,
    # while recording multi-year appearance frequency and longevity.
    # -------------------------------------------------------------
    # Calculate longevity metrics
    appearances = df.groupby(["Name", "Author"]).agg(
        appearance_count=("Year", "count"),
        years_list=("Year", lambda x: sorted(list(x))),
        min_year=("Year", "min"),
        max_year=("Year", "max")
    ).reset_index()

    # Sort so that highest review count (and latest year) appears first
    df_sorted = df.sort_values(by=["Name", "Author", "Reviews", "Year"], ascending=[True, True, False, False])
    unique_titles = df_sorted.drop_duplicates(subset=["Name", "Author"], keep="first").copy()

    # Merge longevity metrics back into unique titles
    unique_titles = unique_titles.merge(appearances, on=["Name", "Author"])

    unique_titles_path = "data/cleaned_unique_titles.csv"
    unique_titles.to_csv(unique_titles_path, index=False)
    print(f"Saved View 2 (Unique Titles): {unique_titles_path} ({len(unique_titles)} books)")

    # -------------------------------------------------------------
    # Step 4: Export Compact JSON for Client-Side Website
    # -------------------------------------------------------------
    export_payload = {
        "metadata": {
            "source": "Kaggle: Amazon Top 50 Bestselling Books 2009-2019",
            "curator": "Sohier Dane / Vijay Choudhary",
            "year_range": [int(df["Year"].min()), int(df["Year"].max())],
            "total_listings": len(df),
            "total_unique_titles": len(unique_titles),
            "categories": sorted(df["Genre"].unique().tolist()),
            "note": "Only Fiction and Non Fiction categories are present from 2009 to 2019. Zero-dollar prices represent promotional or free Kindle editions and are flagged."
        },
        "all_listings": [
            {
                "title": row["Name"],
                "author": row["Author"],
                "rating": float(row["User Rating"]),
                "reviews": int(row["Reviews"]),
                "price": float(row["Price"]),
                "year": int(row["Year"]),
                "genre": row["Genre"]
            }
            for _, row in df.iterrows()
        ],
        "unique_titles": [
            {
                "title": row["Name"],
                "author": row["Author"],
                "rating": float(row["User Rating"]),
                "reviews": int(row["Reviews"]),
                "price": float(row["Price"]),
                "peak_year": int(row["Year"]),
                "genre": row["Genre"],
                "appearances": int(row["appearance_count"]),
                "years": row["years_list"]
            }
            for _, row in unique_titles.iterrows()
        ]
    }

    os.makedirs("site", exist_ok=True)
    site_json_path = "site/data.json"
    with open(site_json_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, separators=(",", ":"))

    file_size_kb = os.path.getsize(site_json_path) / 1024
    print(f"Exported client payload to {site_json_path} ({file_size_kb:.1f} KB)")

    return df, unique_titles


if __name__ == "__main__":
    clean_bestsellers_data()
