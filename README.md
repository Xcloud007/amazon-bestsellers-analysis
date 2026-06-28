<div align="center">

# 📚 Amazon Bestsellers Analysis

### A Python data analysis tool that transforms a CSV of Amazon's bestselling books into a fully interactive, self-contained HTML report — with charts, rankings, and insights. No server required.

<br/>

![Python](https://img.shields.io/badge/Python-3.8+-7C3AED?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-6D28D9?style=for-the-badge&logo=pandas&logoColor=white)
![HTML](https://img.shields.io/badge/Report-Interactive%20HTML-5B21B6?style=for-the-badge&logo=html5&logoColor=white)
![Chart.js](https://img.shields.io/badge/Charts-Chart.js-4C1D95?style=for-the-badge&logo=chartdotjs&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-7C3AED?style=for-the-badge)

<br/>

![Demo Preview](https://img.shields.io/badge/Output-Interactive%20HTML%20Report-8B5CF6?style=flat-square)
&nbsp;
![Data](https://img.shields.io/badge/Dataset-Amazon%20Top%2050%20Books-6D28D9?style=flat-square)
&nbsp;
![Zero Server](https://img.shields.io/badge/Server-Not%20Required-5B21B6?style=flat-square)

</div>

---

## What Is This?

This project reads a `.csv` file containing Amazon's bestselling books and automatically generates a **beautiful, interactive HTML report** that opens directly in your browser.

No dashboards to set up. No servers to run. Just one command — and a full visual analysis appears.

It was built using **Python** and **Pandas** — one of the most widely used data analysis libraries in the world. The output report is powered by **Chart.js**, a JavaScript charting library that creates smooth, interactive visualisations.

---

## Features

- **One-command execution** — run the script and the report opens automatically
- **6 interactive charts** — genre breakdown, books per year, rating distribution, price comparison, top authors, and more
- **2 ranked tables** — Top 10 books by number of reviews, Top 10 books by rating
- **Summary dashboard** — total books, unique authors, average rating, average price at a glance
- **Works with any CSV** — not locked to the sample dataset; bring your own data
- **Zero dependencies for the report** — the HTML file is fully self-contained and shareable
- **Dark luxury UI** — professional purple-themed interface, readable in any browser
- **Smart data cleaning** — automatically handles missing values and inconsistent formatting

---

## Project Structure

```
amazon-bestsellers-analysis/
│
├── analyze.py          ← Main Python script (the brain)
├── bestsellers.csv     ← Sample dataset (50 Amazon bestsellers)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

> `report.html` is generated automatically when you run the script. It is not included in the repository.

---

## Technologies Used

| Technology | Purpose | Version |
|---|---|---|
| **Python** | Core programming language | 3.8+ |
| **Pandas** | Data loading, cleaning, and analysis | 2.0+ |
| **Chart.js** | Interactive charts in the HTML report | 4.4.0 |
| **HTML / CSS / JS** | Report structure, styling, and interactivity | — |
| **argparse** | Command-line argument handling | Built-in |
| **json** | Passing Python data into the HTML report | Built-in |
| **webbrowser** | Auto-opening the report in your browser | Built-in |

---

## Installation & Setup

### Prerequisites

Make sure you have **Python 3.8 or higher** installed.

Check by running:
```bash
python --version
```

If you see `Python 3.x.x` you're good to go. If not, download Python from [python.org](https://www.python.org/downloads/) — make sure to check **"Add Python to PATH"** during installation.

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Xcloud007/amazon-bestsellers-analysis.git
cd amazon-bestsellers-analysis
```

---

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs **Pandas** — the only external library this project needs.

---

### Step 3 — Run the Analysis

```bash
python analyze.py
```

That's it. The report generates and opens in your browser automatically.

---

## Usage

### Basic Usage (uses the included sample dataset)

```bash
python analyze.py
```

### Use Your Own CSV File

```bash
python analyze.py --csv path/to/your_file.csv
```

### Specify a Custom Output File Name

```bash
python analyze.py --csv your_data.csv --out my_report.html
```

---

### CSV Format Requirements

Your CSV file must contain these exact column names:

| Column | Type | Example |
|---|---|---|
| `Name` | Text | The Alchemist |
| `Author` | Text | Paulo Coelho |
| `User Rating` | Decimal | 4.6 |
| `Reviews` | Whole number | 56353 |
| `Price` | Whole number | 10 |
| `Year` | Whole number | 2014 |
| `Genre` | Text | Fiction or Non Fiction |

---

### Where to Get Real Data

The best free dataset for this project is available on Kaggle:

**[Amazon Top 50 Bestselling Books 2009–2019](https://www.kaggle.com/datasets/sootersaalu/amazon-top-50-bestselling-books-2009-2019)**

1. Download `bestsellers with categories.csv`
2. Rename it to `bestsellers.csv`
3. Place it in the project folder
4. Run `python analyze.py`

---

## What the Report Contains

Once generated, the HTML report includes:

```
📊 Overview Cards
   Total Books · Unique Authors · Avg Rating · Avg Price · Avg Reviews · Year Range

📈 Visual Charts
   ├── Genre Distribution         (Donut chart)
   ├── Books Per Year             (Line chart)
   ├── Rating Distribution        (Bar chart — bucketed by range)
   ├── Average Price by Genre     (Bar chart)
   ├── Top Authors by Appearances (Horizontal bar chart)
   └── Average Rating by Genre    (Bar chart)

🏆 Ranked Tables
   ├── Top 10 Books by Number of Reviews
   └── Top 10 Books by User Rating
```

---

## Example Output (Terminal)

```
[1/3] Loading data from 'bestsellers.csv' ...
      50 records loaded.
[2/3] Running analysis ...
      Books: 50  |  Authors: 42  |  Avg Rating: 4.59  |  Avg Price: $10.98
[3/3] Writing report to 'report.html' ...

✓  Report ready → C:\My Folder\Projects\amazon-bestsellers-analysis\report.html
   Opening in browser ...
```

---

## How It Works (Simple Version)

```
bestsellers.csv
      │
      │  pandas reads and cleans all rows
      ▼
analyze.py
      │
      ├── Calculates 9 different analyses
      ├── Converts results to JSON format
      └── Stamps data into HTML template
                    │
                    ▼
              report.html
                    │
              Opens in browser
                    │
         Interactive charts + tables
```

---

## Contributing

Contributions are welcome! If you'd like to improve this project:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a **Pull Request** and describe what you changed

### Ideas for Contributions

- Add more chart types (scatter plot of price vs rating, etc.)
- Support for additional CSV formats and column name variations
- Export report as PDF
- Add filters to the HTML report (filter by year, genre, etc.)
- Dark / light mode toggle in the report

---

## License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it for personal or commercial purposes.

---

<div align="center">

Built with Python and Pandas &nbsp;·&nbsp; by [Rupesh Sharma](https://github.com/Xcloud007)

⭐ If you found this useful, consider starring the repository

</div>
