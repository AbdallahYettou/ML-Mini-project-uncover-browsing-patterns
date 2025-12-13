# Web Usage Mining Mini Project

This project implements web usage mining techniques to analyze server access logs. It uses association rule mining algorithms to discover patterns in user browsing behavior.

## Project Structure

- `app.py`: The main Streamlit application for visualizing results.
- `Data/`: Contains the datasets used for analysis.
- `cleanningData/`: Scripts and modules for preprocessing and cleaning log data.
- `usedAlgorithme/`: Implementation of mining algorithms (Apriori, FP-Growth, etc.).
- `requirements.txt`: List of Python dependencies.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the dashboard application:

```bash
streamlit run app.py
```

## Features

- Data Preprocessing: Cleaning and formatting of raw server logs.
- Association Rule Mining: Application of Apriori, FP-Growth, and ECLAT algorithms.
- Visualization: Interactive dashboard to explore the generated rules and insights.
