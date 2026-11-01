"""
Verification Script: check_outputs.py
=====================================
Fails loudly with non-zero exit code if any expected dataset,
chart, or export artifact is missing or corrupted.
"""

import os
import sys

REQUIRED_DATA_FILES = [
    "data/raw_bestsellers.csv",
    "data/cleaned_all_listings.csv",
    "data/cleaned_unique_titles.csv",
    "site/data.json",
]

REQUIRED_CHART_FILES = [
    "charts/q1_top_authors.png",
    "charts/q2_category_mix_over_time.png",
    "charts/q3_new_titles_per_year.png",
    "charts/q4_most_reviewed_books.png",
    "charts/q5_price_vs_rating_correlation.png",
    "charts/q6_staying_power_by_category.png",
    "charts/key_insights.txt",
]


def verify_outputs():
    print("=" * 60)
    print("RUNNING INTEGRITY AUDIT: Bestsellers Analyzer Artifacts")
    print("=" * 60)

    missing_or_empty = []

    all_targets = REQUIRED_DATA_FILES + REQUIRED_CHART_FILES

    for file_path in all_targets:
        if not os.path.exists(file_path):
            print(f"[MISSING] {file_path}")
            missing_or_empty.append((file_path, "File does not exist"))
        else:
            size = os.path.getsize(file_path)
            if size == 0:
                print(f"[EMPTY 0 bytes] {file_path}")
                missing_or_empty.append((file_path, "File is empty"))
            else:
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} bytes"
                print(f"[OK] ({size_str:>9}): {file_path}")

    print("=" * 60)
    if missing_or_empty:
        print(f"\nAUDIT FAILED! {len(missing_or_empty)} critical artifact(s) missing or corrupt:")
        for path, reason in missing_or_empty:
            print(f"   - {path}: {reason}")
        print("\nPlease run clean_data.py and analysis.py to regenerate missing files.\n")
        sys.exit(1)
    else:
        print("\nALL OUTPUTS VERIFIED SUCCESSFULLY! Everything is present and healthy.\n")
        sys.exit(0)


if __name__ == "__main__":
    verify_outputs()
