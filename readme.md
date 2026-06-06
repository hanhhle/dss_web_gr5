# 🚀 Enterprise Marketing Decision Support System (DSS) - Group 5

Welcome to the **Decision Support System for Enterprise Marketing Campaigns**. This interactive web-based dashboard is designed to help B2B Marketing Managers and Telesales teams optimize their campaigns through Data Mining and Machine Learning techniques.

## 🌟 Key Features

This DSS guides decision-makers through 3 main analytical stages:
1. **Market Overview & Segmentation (Descriptive Analytics):** Uses K-Means Clustering to group corporate customers based on their IT Budgets and Historical Spend.
2. **Targeted Sales Engine (Predictive Analytics):** Uses Decision Trees to identify "Hot Leads" (Probability > 60%) for specific campaigns, helping telesales prioritize who to call.
3. **Smart Cross-Sell Strategy (Prescriptive Analytics):** Uses the Apriori Algorithm to generate dynamic product bundles, recommending exactly what to upsell based on the customer's current IT stack.

## 🗂️ Project Structure

- `app.py`: The main Streamlit web application.
- `Two_Stage_Clustered_B2B_Data.csv`: Pre-processed dataset with K-Means segmentation labels.
- `MASTER_Hot_Leads_All_Campaigns.csv`: Extracted hot leads with predicted buying probabilities.
- `MASTER_Cross_Sell_Rules_All_Campaigns.xlsx`: Generated cross-selling rules.
- `requirements.txt`: List of Python dependencies.

---

## 🛠️ Setup & Installation Guide

Follow these steps to run the application on your local machine.

### Prerequisites
Make sure you have [Python 3.8+](https://www.python.org/downloads/) installed.

### 1. Clone the repository
Open your terminal/command prompt and run:
```bash
git clone <YOUR_GITHUB_REPO_URL_HERE>
cd dss_web_gr5

### 2. Set up a Virtual Environment
It is highly recommended to use a virtual environment to avoid package conflicts.

For Mac/Linux:
Bash
python3 -m venv .venv
source .venv/bin/activate

For Windows (Command Prompt):
DOS
python -m venv .venv
.venv\Scripts\activate

### 3. Install Dependencies
Install all required libraries using pip:

Bash
pip install -r requirements.txt

### 4. Run the Application
Start the Streamlit server:

Bash
streamlit run app.py
The application will automatically open in your default web browser at http://localhost:8501.

💡 How to use the Dashboard
Navigate to the Customer Segmentation tab to view the financial distribution of corporate clusters.

Go to the Prediction & Targeted Sales tab, select a Campaign and a Customer Segment to generate a downloadable target list for the Telesales team.

Open the Recommended Strategy tab, use the filters to select what the customer already owns, and instantly get data-driven cross-sell recommendations.

Project built for Data Analytics and Decision Making Course - Group 5.