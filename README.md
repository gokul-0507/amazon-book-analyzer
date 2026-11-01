# Amazon Bestseller Trends & Literary Analytics (2009–2019)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end data science and front-end engineering platform that analyzes Amazon's Top 50 Bestselling Books from 2009 to 2019. The project includes automated data cleaning, publication-grade analytical figures (300 DPI), a browser-based interactive exploration dashboard with zero-latency client-side filtering, and an optional companion Streamlit application.

---

## 📖 Table of Contents
1. [Empirical Scope & Honest Data Limits](#empirical-scope--honest-data-limits)
2. [Project Architecture & Structure](#project-architecture--structure)
3. [Setup & Installation](#setup--installation)
4. [Running the Data Pipeline](#running-the-data-pipeline)
5. [Visualizations & Research Insights](#visualizations--research-insights)
6. [Interactive Web Applications](#interactive-web-applications)
7. [Deployment Guide (GitHub Pages & Streamlit Cloud)](#deployment-guide)
8. [Live Deployment Verification Checklist](#live-deployment-verification-checklist)

---

## 🎯 Empirical Scope & Honest Data Limits

This platform is strictly scoped to the empirical boundaries of the **Kaggle Amazon Top 50 Bestselling Books (2009–2019)** dataset curated by Sohier Dane and Vijay Choudhary:

- **Row Count**: Strictly **550 records** (50 titles charted per year across 11 calendar years).
- **Date Range**: Strictly **2009 to 2019**. The dataset contains no records prior to 2009 or after 2019.
- **Taxonomy**: Limited strictly to two macro genres: **Fiction** and **Non Fiction**. Subgenres (such as cookbooks, business guides, YA fantasy, and memoirs) are nested under these two umbrellas.
- **Pricing Caveat**: 12 records show `$0.00` price. These represent promotional Kindle giveaways or zero-cost editions (e.g. *To Kill a Mockingbird*, *Frozen*). They are preserved in the raw archive but excluded from regression fits and pricing averages.
- **Reviews Caveat**: Amazon customer review numbers capture peak historical snapshots at listing time rather than real-time cumulative sales or inventory metrics.

---

## 📁 Project Architecture & Structure

```text
amazon-book-analyzer/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules (protects .env, venv, pycache)
├── requirements.txt          # Python dependencies
├── clean_data.py             # Data cleaning and dual-view generation pipeline
├── analysis.py               # Statistical computations and 300 DPI chart generator
├── check_outputs.py          # Output integrity auditor (fails loudly if artifacts miss)
├── test_project.py           # Automated unit test suite
├── app.py                    # Reactive companion Streamlit application
├── data/
│   ├── raw_bestsellers.csv         # 550 raw scraped Kaggle records
│   ├── cleaned_all_listings.csv    # View 1: 550 cleaned time-series records
│   └── cleaned_unique_titles.csv   # View 2: 347 deduplicated books with longevity metrics
├── charts/
│   ├── q1_top_authors.png                  # Q1: Top 10 authors by unique bestsellers
│   ├── q2_category_mix_over_time.png       # Q2: Category mix and annual shares
│   ├── q3_new_titles_per_year.png          # Q3: Roster turnover / fresh entrants per year
│   ├── q4_most_reviewed_books.png          # Q4: Top 10 most reviewed bestsellers
│   ├── q5_price_vs_rating_correlation.png  # Q5: Price vs rating scatter and regression
│   ├── q6_staying_power_by_category.png    # Q6: Shelf longevity distributions
│   └── key_insights.txt                    # Auto-generated dynamic data summary
└── site/
    ├── index.html            # Static responsive web explorer (Tailwind + SVG + Vanilla JS)
    └── data.json             # Compact JSON database for 100% browser-based filtering
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/gokul-0507/amazon-book-analyzer.git
cd amazon-book-analyzer
```

### 2. Configure Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install exact requirements
pip install -r requirements.txt
```

---

## 🚀 Running the Data Pipeline

### Step 1: Clean Raw Data and Generate Dual Views
Executes title casing standardization, author name reconciliation (*George R.R. Martin* $\rightarrow$ *George R. R. Martin*, *J.K. Rowling* $\rightarrow$ *J. K. Rowling*), computes book longevity, and generates `site/data.json`:
```bash
python clean_data.py
```

### Step 2: Generate Publication-Grade 300 DPI Visualizations
Computes statistics and exports all 6 research charts to `charts/`:
```bash
python analysis.py
```

### Step 3: Run Integrity Audit & Unit Tests
Verifies that all data files and figures exist and meet schema requirements:
```bash
python check_outputs.py
python test_project.py
```

---

## 📊 Visualizations & Research Insights

All figures are saved in `charts/` at 300 DPI with publication-standard typography and accessible color palettes:

1. **Q1: Which authors have the most unique bestsellers?**
   - **Jeff Kinney** leads with 12 unique titles (*Diary of a Wimpy Kid* franchise), followed by **Rick Riordan** (10) and **J. K. Rowling** (8).
2. **Q2: Category Mix Over Time (2009–2019)**
   - Non Fiction held the majority share across 10 of the 11 charted years (overall 56.4% share), peaking in 2015 at 66%. Fiction briefly overtook in 2014 (58%).
3. **Q3: Annual Roster Turnover & New Entrants**
   - Following the 2009 baseline (49 unique titles), an average of **29.8 brand-new books** charted each year, indicating robust commercial circulation.
4. **Q4: Top 10 Most Reviewed Bestsellers**
   - Led by *Where the Crawdads Sing* (87,841 reviews, 4.8★), followed by *The Girl on the Train* (79,446 reviews, 4.1★) and *Becoming* (61,133 reviews, 4.8★).
5. **Q5: Relationship Between Book Price and User Rating**
   - Pearson correlation coefficient is **$r = -0.12$**. There is negligible correlation between book pricing and reader satisfaction.
6. **Q6: Staying Power Comparison Across Categories**
   - Non Fiction books enjoy slightly longer longevity on average (1.63 years vs 1.53 years for Fiction), with reference perennials (*Publication Manual of the APA*) charting for 10 consecutive years.

---

## 🌐 Interactive Web Applications

### Option A: Static Web Explorer (`site/index.html`)
The primary website is a zero-dependency, client-side web application built with **Tailwind CSS**, **Newsreader Serif**, and **vanilla JavaScript**.
All filtering runs in the visitor's browser with no server required.

To run locally:
```bash
# Serve the site directory on localhost port 8000
python -m http.server 8000 -d site
```
Then open [http://localhost:8000](http://localhost:8000) in your web browser.

**Key Features**:
- **Sticky Controls Bar**: Synchronized dual-thumb year slider, Fiction/Non Fiction toggle chips, and instant author/title search.
- **Interactive Filtering**: Clicking any author's bar in the leaderboard instantly filters all metrics, charts, and tables to that creator.
- **Sortable Catalog**: Instant client-side sorting by rating, review count, price, or longevity.
- **Robust State Handling**: Dedicated animated loading state, contextual empty state with 1-click filter reset, and error fallback.

### Option B: Companion Streamlit Application (`app.py`)
For an interactive Python-native dashboard experience:
```bash
streamlit run app.py
```

---

## 🚢 Deployment Guide

### 1. Deploying the Static Site to GitHub Pages

1. Push all code to your GitHub repository:
   ```bash
   git add .
   git commit -m "feat: complete bestseller analysis engine, charts, and interactive site"
   git push -u origin main
   ```
2. Open your repository on GitHub: `https://github.com/gokul-0507/amazon-book-analyzer`
3. Click on **Settings** $\rightarrow$ **Pages** (under the "Code and automation" left sidebar).
4. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Select `main`, and choose folder `/site` (or `/` if you copy `index.html` to root, or use GitHub Actions).
   - *Note*: If GitHub Pages only offers `/ (root)` and `/docs` in branch dropdown:
     - Simply copy `site/*` into a `docs/` folder or root, commit, and select `/docs`.
5. Click **Save**.
6. Within 1–2 minutes, your website will be live at:
   `https://gokul-0507.github.io/amazon-book-analyzer/`

### 2. Deploying to Streamlit Community Cloud

1. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2. Click **New app**.
3. Select your repository: `gokul-0507/amazon-book-analyzer`.
4. Set the **Main file path** to `app.py`.
5. Click **Deploy**. Your interactive Streamlit app will go live with an automatic public URL.

---

## ✅ Live Deployment Verification Checklist

Once deployed, open your live URL in an incognito / private browser window and verify:

- [ ] **Initial Page Load**: Masthead loads with *Newsreader* serif headings; all headline metrics render instantly ($550$ listings, $347$ unique books, $4.62$ rating, $\$13.39$ price).
- [ ] **Year Slider Reactivity**: Dragging the year slider to `2012–2016` immediately updates all metrics, charts, and table rows.
- [ ] **Category Chips**: Clicking `Fiction` off updates the view to Non Fiction only; toggling it back restores full data.
- [ ] **Author Cross-Filtering**: Clicking *Jeff Kinney* in the Q1 chart filters the dashboard strictly to his titles.
- [ ] **Empty State**: Unselecting both categories displays the empty-state banner explaining why and provides a functional "Reset All Filters" button.
- [ ] **Table Sorting**: Clicking table headers (Reviews, Price, Rating) sorts the table ascending and descending.
- [ ] **Mobile Responsiveness**: Test on mobile view; controls remain accessible and sticky at the top of the viewport.
- [ ] **Security**: Inspect `.git` logs to confirm no `.env` or sensitive API keys are exposed.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
