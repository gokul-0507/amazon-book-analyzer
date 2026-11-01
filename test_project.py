"""
Automated Test Suite for Bestsellers Project
============================================
Validates data integrity, mathematical constraints, and output structure.
"""

import json
import os
import unittest
import pandas as pd


class TestBestsellersProject(unittest.TestCase):

    def test_raw_data_shape(self):
        df = pd.read_csv("data/raw_bestsellers.csv")
        self.assertEqual(len(df), 550, "Raw dataset must contain exactly 550 rows.")
        self.assertEqual(set(df["Genre"].unique()), {"Fiction", "Non Fiction"})
        self.assertEqual(df["Year"].min(), 2009)
        self.assertEqual(df["Year"].max(), 2019)

    def test_cleaned_all_listings(self):
        df = pd.read_csv("data/cleaned_all_listings.csv")
        self.assertEqual(len(df), 550, "All listings view must maintain all 550 rows.")
        # Ensure author standardization
        self.assertNotIn("George R.R. Martin", df["Author"].values)
        self.assertNotIn("J.K. Rowling", df["Author"].values)
        self.assertIn("George R. R. Martin", df["Author"].values)
        self.assertIn("J. K. Rowling", df["Author"].values)

    def test_cleaned_unique_titles(self):
        df = pd.read_csv("data/cleaned_unique_titles.csv")
        self.assertLess(len(df), 550, "Unique titles must be deduplicated.")
        self.assertTrue(df["appearance_count"].min() >= 1)
        self.assertTrue(df["Reviews"].min() >= 0)

    def test_site_json_structure(self):
        with open("site/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("metadata", data)
        self.assertIn("all_listings", data)
        self.assertIn("unique_titles", data)
        self.assertEqual(len(data["all_listings"]), 550)
        self.assertEqual(data["metadata"]["year_range"], [2009, 2019])

    def test_charts_exist_and_non_empty(self):
        chart_files = [
            "charts/q1_top_authors.png",
            "charts/q2_category_mix_over_time.png",
            "charts/q3_new_titles_per_year.png",
            "charts/q4_most_reviewed_books.png",
            "charts/q5_price_vs_rating_correlation.png",
            "charts/q6_staying_power_by_category.png",
            "charts/key_insights.txt"
        ]
        for f in chart_files:
            self.assertTrue(os.path.exists(f), f"File missing: {f}")
            min_size = 100 if f.endswith(".txt") else 1000
            self.assertGreater(os.path.getsize(f), min_size, f"File too small: {f}")

    def test_no_secrets_in_repo(self):
        # Scan files for accidental API key commits
        for fname in [".env.example", "requirements.txt", "README.md", "clean_data.py", "analysis.py", "app.py"]:
            if os.path.exists(fname):
                with open(fname, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    self.assertNotIn("AIza", content)
                    self.assertNotIn("sk-", content)


if __name__ == "__main__":
    unittest.main()
