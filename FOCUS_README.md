
# FOCUS - Financial Oversight & Clarity for Unified Spending

FOCUS is a financial insights application designed for the Army Research Laboratory (ARL) to monitor, assess, and project fiscal solvency across divisions. The app integrates multiple financial data sources and provides leadership with interactive dashboards, GPT-driven narratives, and scenario-based solvency projections.

## Key Features

- **FY25 Plan vs Actuals**: Compare planned funding targets against actual spending across divisions.
- **Non-Labor Detail**: Analyze non-labor expenses, vendor breakdowns, and category-based trends.
- **Status of Funds**: Monitor current commitments, allotments, and available funding by division.
- **Scenario Planner**: Simulate funding adjustments across categories to evaluate solvency impact.
- **Solvency Projections**: Project end-of-year solvency based on labor forecasts and non-labor commitments.

## App Structure

1. **FY25 Plan**: Displays planned funding targets with solvency calculations.
2. **FY25 Actuals**: Visualizes current spending and compares to planned targets.
3. **FY25 Actuals NL Detail**: Breaks down non-labor expenses by category and vendor.
4. **Status of Funds**: Shows current commitments and available funding.
5. **ScenarioSolvency**: Enables leadership to model funding adjustments and view projected solvency.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/focus.git
   cd focus
   ```

2. **Create Virtual Environment (Optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App Locally**
   ```bash
   streamlit run focus.py
   ```

5. **Prepare Data Files**

   - Ensure the input Excel file contains the following sheets:
     - `Status of Funds`
     - `WBS Category Breakout`
     - `IOB Recap ReportPlan`
     - `Non Labor Detail`

   - Place the Excel file in the app's root directory or upload it via the app interface.

## Dependencies

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- OpenAI (for GPT-based insights)
- Other dependencies listed in `requirements.txt`

## Deployment

You can deploy FOCUS via **Streamlit Cloud** or other hosting platforms. For Streamlit Cloud:

1. Push your repository to GitHub.
2. Connect your GitHub repo to Streamlit Cloud.
3. Set the **main file path** to `focus.py`.
4. Configure any environment variables (e.g., OpenAI API key) as needed.

## License

This project is proprietary and intended for internal use by the Army Research Laboratory.
