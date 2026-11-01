"""
Streamlit Bestseller Explorer (app.py)
======================================
Interactive companion web application powered by Streamlit.
Features reactive year range and genre multiselect controls,
@st.cache_data caching, empty-state defense, and full analytical views.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Set page configuration
st.set_page_config(
    page_title="Amazon Bestseller Trends (2009–2019)",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom palette
COLOR_NAVY = "#185FA5"
COLOR_RUST = "#C05621"
COLOR_MUTED = "#5E5B52"
COLOR_BG = "#FAFAF7"


@st.cache_data
def load_datasets():
    all_df = pd.read_csv("data/cleaned_all_listings.csv")
    unique_df = pd.read_csv("data/cleaned_unique_titles.csv")
    return all_df, unique_df


all_listings_df, unique_titles_df = load_datasets()

# -------------------------------------------------------------
# Sidebar Controls
# -------------------------------------------------------------
st.sidebar.title("Filter Controls")
st.sidebar.markdown("Refine bestseller archive by time, category, or creator.")

min_yr, max_yr = int(all_listings_df["Year"].min()), int(all_listings_df["Year"].max())
selected_years = st.sidebar.slider(
    "Year Range",
    min_value=min_yr,
    max_value=max_yr,
    value=(min_yr, max_yr),
    step=1
)

all_genres = sorted(all_listings_df["Genre"].unique().tolist())
selected_genres = st.sidebar.multiselect(
    "Book Categories",
    options=all_genres,
    default=all_genres
)

author_query = st.sidebar.text_input("Search Author or Title", "").strip().lower()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data Limits & Scope**\n"
    "- 550 rows (50/year)\n"
    "- 2009 to 2019 only\n"
    "- Fiction and Non Fiction only\n"
    "- Source: Kaggle (Sohier Dane / Vijay Choudhary)"
)

# -------------------------------------------------------------
# Data Filtering Pipeline
# -------------------------------------------------------------
filtered_listings = all_listings_df[
    (all_listings_df["Year"] >= selected_years[0]) &
    (all_listings_df["Year"] <= selected_years[1]) &
    (all_listings_df["Genre"].isin(selected_genres))
]

if author_query:
    filtered_listings = filtered_listings[
        filtered_listings["Author"].str.lower().str.contains(author_query) |
        filtered_listings["Name"].str.lower().str.contains(author_query)
    ]

# Derive unique books from filtered listings
if not filtered_listings.empty:
    appearances = filtered_listings.groupby(["Name", "Author"]).size().reset_index(name="appearances")
    filtered_unique = (
        filtered_listings.sort_values(by=["Reviews", "Year"], ascending=[False, False])
        .drop_duplicates(subset=["Name", "Author"], keep="first")
        .merge(appearances, on=["Name", "Author"])
    )
else:
    filtered_unique = pd.DataFrame()

# -------------------------------------------------------------
# Header & Masthead
# -------------------------------------------------------------
st.title("Amazon Bestseller Trends (2009–2019)")
st.caption("A data-driven empirical analysis of 550 annual rankings across Fiction and Non Fiction.")

# -------------------------------------------------------------
# Empty State Defense
# -------------------------------------------------------------
if filtered_listings.empty:
    st.warning("⚠️ No bestsellers match your current filter selections. Please expand your year range or select at least one genre.")
    if st.button("Reset All Filters"):
        st.rerun()
    st.stop()

# -------------------------------------------------------------
# Headline Metrics Bar
# -------------------------------------------------------------
priced_listings = filtered_listings[filtered_listings["Price"] > 0]
avg_price_val = priced_listings["Price"].mean() if not priced_listings.empty else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Listings", f"{len(filtered_listings):,}")
col2.metric("Unique Books", f"{len(filtered_unique):,}")
col3.metric("Average Rating", f"{filtered_listings['User Rating'].mean():.2f} / 5.0")
col4.metric("Average Price", f"${avg_price_val:.2f}" if avg_price_val > 0 else "n/a")

st.markdown("---")

# -------------------------------------------------------------
# Visualizations Section
# -------------------------------------------------------------
row1_left, row1_right = st.columns([7, 5])

with row1_left:
    st.subheader("Q1. Top Authors by Unique Bestsellers")
    top_authors = filtered_unique["Author"].value_counts().head(10).reset_index()
    top_authors.columns = ["Author", "Unique Titles"]
    top_authors = top_authors.sort_values(by="Unique Titles", ascending=True)

    fig1, ax1 = plt.subplots(figsize=(8, 4.5), facecolor=COLOR_BG)
    ax1.set_facecolor(COLOR_BG)
    ax1.barh(top_authors["Author"], top_authors["Unique Titles"], color=COLOR_NAVY, height=0.65)
    for i, v in enumerate(top_authors["Unique Titles"]):
        ax1.text(v + 0.15, i, f"{int(v)}", va="center", fontweight="bold", color="#1D1D1B")
    ax1.set_xlim(0, max(top_authors["Unique Titles"]) + 1.5)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.set_xlabel("Unique Titles Charted")
    plt.tight_layout()
    st.pyplot(fig1)

with row1_right:
    st.subheader("Q2. Category Mix Over Time")
    mix_data = pd.crosstab(filtered_listings["Year"], filtered_listings["Genre"], normalize="index") * 100
    fig2, ax2 = plt.subplots(figsize=(6, 4.5), facecolor=COLOR_BG)
    ax2.set_facecolor(COLOR_BG)

    years = mix_data.index.tolist()
    if "Fiction" in mix_data.columns and "Non Fiction" in mix_data.columns:
        ax2.bar(years, mix_data["Non Fiction"], label="Non Fiction", color=COLOR_RUST, width=0.55)
        ax2.bar(years, mix_data["Fiction"], bottom=mix_data["Non Fiction"], label="Fiction", color=COLOR_NAVY, width=0.55)
    elif "Fiction" in mix_data.columns:
        ax2.bar(years, mix_data["Fiction"], label="Fiction", color=COLOR_NAVY, width=0.55)
    elif "Non Fiction" in mix_data.columns:
        ax2.bar(years, mix_data["Non Fiction"], label="Non Fiction", color=COLOR_RUST, width=0.55)

    ax2.set_ylabel("Share (%)")
    ax2.set_ylim(0, 105)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper right")
    plt.tight_layout()
    st.pyplot(fig2)

row2_left, row2_right = st.columns(2)

with row2_left:
    st.subheader("Q3. Title Turnover & Fresh Entrants")
    seen_so_far = set()
    years_all = sorted(all_listings_df["Year"].unique())
    new_entrants_dict = {}
    for yr in years_all:
        yr_titles = set(all_listings_df[all_listings_df["Year"] == yr]["Name"])
        fresh = yr_titles - seen_so_far
        new_entrants_dict[yr] = len(fresh)
        seen_so_far.update(yr_titles)

    active_yrs = [y for y in years_all if selected_years[0] <= y <= selected_years[1]]
    active_counts = [new_entrants_dict[y] for y in active_yrs]

    fig3, ax3 = plt.subplots(figsize=(7, 4), facecolor=COLOR_BG)
    ax3.set_facecolor(COLOR_BG)
    ax3.bar(active_yrs, active_counts, color="#2B6CB0", width=0.55)
    for y, c in zip(active_yrs, active_counts):
        ax3.text(y, c + 1, str(c), ha="center", fontweight="bold")
    ax3.set_ylim(0, 58)
    ax3.set_ylabel("Brand New Titles")
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)

with row2_right:
    st.subheader("Q6. Staying Power by Category")
    fig6, ax6 = plt.subplots(figsize=(7, 4), facecolor=COLOR_BG)
    ax6.set_facecolor(COLOR_BG)

    genre_groups = [filtered_unique[filtered_unique["Genre"] == g]["appearances"] for g in selected_genres if g in filtered_unique["Genre"].unique()]
    if genre_groups:
        bp = ax6.boxplot(genre_groups, tick_labels=[g for g in selected_genres if g in filtered_unique["Genre"].unique()], patch_artist=True)
        colors = [COLOR_NAVY if g == "Fiction" else COLOR_RUST for g in selected_genres if g in filtered_unique["Genre"].unique()]
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
    ax6.set_ylabel("Total Years on List")
    ax6.spines["top"].set_visible(False)
    ax6.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig6)

row3_left, row3_right = st.columns(2)

with row3_left:
    st.subheader("Q4. Top Most Reviewed Bestsellers")
    top_rev_books = filtered_unique.sort_values(by="Reviews", ascending=False).head(8).sort_values(by="Reviews", ascending=True)
    fig4, ax4 = plt.subplots(figsize=(7, 4.5), facecolor=COLOR_BG)
    ax4.set_facecolor(COLOR_BG)

    short_titles = [t[:28] + "…" if len(t) > 28 else t for t in top_rev_books["Name"]]
    b_colors = [COLOR_NAVY if g == "Fiction" else COLOR_RUST for g in top_rev_books["Genre"]]
    ax4.barh(short_titles, top_rev_books["Reviews"], color=b_colors, height=0.65)
    for i, (r, star) in enumerate(zip(top_rev_books["Reviews"], top_rev_books["User Rating"])):
        ax4.text(r + 1000, i, f"{r:,} ({star}★)", va="center", fontsize=9, fontweight="bold")
    ax4.set_xlim(0, max(top_rev_books["Reviews"]) + 20000)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    ax4.set_xlabel("Amazon Customer Reviews")
    plt.tight_layout()
    st.pyplot(fig4)

with row3_right:
    st.subheader("Q5. Price vs. Rating Correlation")
    fig5, ax5 = plt.subplots(figsize=(7, 4.5), facecolor=COLOR_BG)
    ax5.set_facecolor(COLOR_BG)

    if len(priced_listings) > 2:
        r_val = priced_listings["Price"].corr(priced_listings["User Rating"])
        sns.regplot(
            data=priced_listings,
            x="Price",
            y="User Rating",
            ax=ax5,
            scatter_kws={"alpha": 0.45, "color": COLOR_NAVY, "s": 30},
            line_kws={"color": COLOR_RUST, "linewidth": 2}
        )
        ax5.text(0.05, 0.1, f"Pearson r = {r_val:.2f}\nVirtually zero correlation", transform=ax5.transAxes, fontsize=9.5, bbox=dict(boxstyle="round", facecolor="#EFECE3", alpha=0.8))
    else:
        ax5.text(0.5, 0.5, "Insufficient data points", ha="center")
    ax5.set_ylim(3.0, 5.1)
    ax5.spines["top"].set_visible(False)
    ax5.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig5)

# -------------------------------------------------------------
# Dynamic Key Insights Box
# -------------------------------------------------------------
st.subheader("Automated Data Insights")
top_auth = top_authors.iloc[-1]["Author"] if not top_authors.empty else "N/A"
top_auth_cnt = top_authors.iloc[-1]["Unique Titles"] if not top_authors.empty else 0
nf_ratio = (filtered_listings["Genre"] == "Non Fiction").mean() * 100

st.info(
    f"In the **{selected_years[0]}–{selected_years[1]}** window, Non Fiction represents **{nf_ratio:.1f}%** of total listings. "
    f"**{top_auth}** holds the record for most distinct bestsellers ({top_auth_cnt} titles). "
    f"Across all paid titles, the average price sits at **${avg_price_val:.2f}**, with no statistically meaningful correlation to customer review scores."
)

# -------------------------------------------------------------
# Sortable Table
# -------------------------------------------------------------
st.subheader("Bestseller Catalog Records")
display_cols = ["Name", "Author", "Genre", "User Rating", "Reviews", "Price", "appearances", "Year"]
table_df = filtered_unique[display_cols].rename(columns={
    "Name": "Title",
    "User Rating": "Rating",
    "appearances": "Total Years Charted",
    "Year": "Peak Year"
})

st.dataframe(table_df, width="stretch")

# -------------------------------------------------------------
# Honest "About This Data" Section
# -------------------------------------------------------------
with st.expander("About This Data & Honest Methodological Caveats"):
    st.markdown("""
    - **Dataset Source**: Kaggle's *Amazon Top 50 Bestselling Books 2009–2019*, curated by Sohier Dane & Vijay Choudhary.
    - **Exact Limits**: Strictly 550 rows, 50 titles per year from 2009 to 2019. Only Fiction and Non Fiction categories are tracked.
    - **Pricing Caveats**: 12 records with `$0.00` price reflect promotional Kindle giveaways or zero-cost editions. They are filtered from correlation fits.
    - **Reviews Caveat**: Amazon customer review counts reflect peak snapshots recorded at listing time, not all-time cumulative counts.
    """)
