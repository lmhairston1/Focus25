import streamlit as st

st.set_page_config(page_title="FOCUS", layout="wide")
st.title("FOCUS – Financial Oversight & Clarity for Unified Spending")
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load data (placeholder for Streamlit file uploader)
uploaded_file = st.file_uploader("Upload FY25 SOF Report.xlsx", type="xlsx")

if uploaded_file:
    xl = pd.ExcelFile(uploaded_file)

    # Load sheets
    plan_df = xl.parse("IOB Recap ReportPlan")
    wbs_df = xl.parse("WBS Category Breakout")
    nl_df = xl.parse("Non Labor Detail")
    sof_df = xl.parse("Status of Funds")

    # Clean headers
    plan_df.columns = plan_df.columns.str.strip()
    wbs_df.columns = wbs_df.columns.str.strip()
    nl_df.columns = nl_df.columns.str.strip()
    sof_df.columns = sof_df.columns.str.strip()

    # Forward-fill key columns
    for df in [plan_df, wbs_df, nl_df, sof_df]:
        df[['Directorate', 'Division', 'FundType']] = df[['Directorate', 'Division', 'FundType']].ffill()

    # Sidebar filters
    directorates = sorted(plan_df['Directorate'].dropna().unique())
    divisions = sorted(plan_df['Division'].dropna().unique())
    fundtypes = sorted(plan_df['FundType'].dropna().unique())

    selected_directorates = st.sidebar.selectbox("Select Directorate", ['All'] + directorates)
    selected_divisions = st.sidebar.selectbox("Select Division", ['All'] + divisions)
    selected_fundtypes = st.sidebar.selectbox("Select FundType", ['All'] + fundtypes)

    # Filter function
    def apply_filters(df):
        return df[
            (df['Directorate'] == selected_directorates if selected_directorates != 'All' else pd.Series([True] * len(df))) &
            (df['Division'] == selected_divisions if selected_divisions != 'All' else pd.Series([True] * len(df))) &
            (df['FundType'] == selected_fundtypes if selected_fundtypes != 'All' else pd.Series([True] * len(df)))
        ]

    # Apply filters
    plan_df = apply_filters(plan_df)
    wbs_df = apply_filters(wbs_df)
    nl_df = apply_filters(nl_df)
    sof_df = apply_filters(sof_df)

    tabs = st.tabs(["FY25 Plan", "FY25 Actuals", "FY25 Actuals NL Detail", "Status of Funds", "Scenario Planner", "ScenarioSolvency"])

    # ---------------- Tab 1: FY25 Plan ----------------
    with tabs[0]:
        st.header("FY25 Plan")
        expense_cols = ['TOTAL LABOR & OH', 'Recruits Labor', 'Recruits OH', 'Recruits Lab & OH',
                        'Travel', 'Training', 'Supplies', 'Contracts', 'OGAs', 'Equip', 'IDX',
                        'DIR-IND', 'HRPP', 'Other', 'Shop']
        plan_df[expense_cols] = plan_df[expense_cols].fillna(0)
        grouped_plan = plan_df.groupby(['Directorate', 'Division'], as_index=False).agg({
            'FY TARGET $ 100%': 'sum', **{col: 'sum' for col in expense_cols}
        })
        grouped_plan['Solvency'] = grouped_plan['FY TARGET $ 100%'] - grouped_plan[expense_cols].sum(axis=1)
        numeric_cols = grouped_plan.select_dtypes(include='number').columns
        st.dataframe(grouped_plan.style.format({col: "${:,.2f}" for col in numeric_cols}))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(grouped_plan['Division'], grouped_plan['Solvency'], color=['green' if x >= 0 else 'red' for x in grouped_plan['Solvency']])
        ax.set_title('Solvency by Division')
        ax.axhline(0, color='black', linewidth=0.8)
        st.pyplot(fig)
        for _, row in grouped_plan.iterrows():
            status = "solvent" if row['Solvency'] >= 0 else "insolvent"
            st.write(f"**{row['Division']} Division** is projected to be **{status}** with a solvency of **${row['Solvency']:,.2f}**.")

    # ---------------- Tab 2: FY25 Actuals ----------------
    with tabs[1]:
        st.header("FY25 Actuals")
        pivot_wbs = wbs_df.pivot_table(index=['Directorate', 'Division'], columns='Category', values='Cum Comm', aggfunc='sum', fill_value=0).reset_index()
        pivot_wbs = pivot_wbs.loc[~pivot_wbs['Division'].isin(['Subtotal:', 'Grand Total:', 'UNKNOWN'])]
        pivot_wbs['Total Expenses'] = pivot_wbs.drop(columns=['Directorate', 'Division']).sum(axis=1)
        numeric_cols = pivot_wbs.select_dtypes(include='number').columns
        st.dataframe(pivot_wbs.style.format({col: "${:,.2f}" for col in numeric_cols}))
        categories = [col for col in pivot_wbs.columns if col not in ['Directorate', 'Division', 'Total Expenses']]
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot_wbs.set_index('Division')[categories].plot(kind='bar', stacked=True, ax=ax)
        ax.set_ylabel("Total Expenses ($)")
        ax.set_title("Actual Expenses by Division and Category")
        st.pyplot(fig)
        for _, row in pivot_wbs.iterrows():
            st.write(f"**{row['Division']} Division** has total actual expenses of **${row['Total Expenses']:,.2f}**.")

    # ---------------- Tab 3: FY25 Actuals NL Detail ----------------
    with tabs[2]:
        st.header("FY25 Actuals NL Detail")
        nl_df['Vendor Name'] = nl_df.apply(lambda row: row['Category'] if pd.isna(row['Vendor Name']) else row['Vendor Name'], axis=1)
        nl_df['Vendor Name'] = nl_df['Vendor Name'].replace('U.S. BANCORP', 'Credit Card Purchase')
        grouped_nl = nl_df.groupby(['Directorate', 'Division', 'Category'], as_index=False)['Cum Comm'].sum()
        pivot_nl = grouped_nl.pivot_table(index=['Directorate', 'Division'], columns='Category', values='Cum Comm', aggfunc='sum', fill_value=0).reset_index()
        pivot_nl = pivot_nl.loc[~pivot_nl['Division'].isin(['UNKNOWN'])]
        pivot_nl['Total Expenses'] = pivot_nl.drop(columns=['Directorate', 'Division']).sum(axis=1)
        numeric_cols = pivot_nl.select_dtypes(include='number').columns
        st.dataframe(pivot_nl.style.format({col: "${:,.2f}" for col in numeric_cols}))
        nl_categories = [col for col in pivot_nl.columns if col not in ['Directorate', 'Division', 'Total Expenses']]
        colors = ["#A9A9A9" if cat == 'Contracts' else plt.cm.tab20.colors[i % 20] for i, cat in enumerate(nl_categories)]
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot_nl.set_index('Division')[nl_categories].plot(kind='bar', stacked=True, ax=ax, color=colors)
        ax.set_ylabel("Non-Labor Expenses ($)")
        ax.set_title("Non-Labor Expenses by Division and Category")
        st.pyplot(fig)
        for _, row in pivot_nl.iterrows():
            st.write(f"**{row['Division']} Division** has total non-labor expenses of **${row['Total Expenses']:,.2f}**.")

    # ---------------- Tab 4: Status of Funds ----------------
    with tabs[3]:
        st.header("Status of Funds")
        sof_df[['Allotment', 'Commitments']] = sof_df[['Allotment', 'Commitments']].fillna(0)
        sof_df['Available'] = sof_df['Allotment'] - sof_df['Commitments']
        grouped_sof = sof_df.groupby(['Directorate', 'Division'], as_index=False).agg({
            'Allotment': 'sum', 'Commitments': 'sum', 'Available': 'sum'
        })
        numeric_cols = grouped_sof.select_dtypes(include='number').columns
        st.dataframe(grouped_sof.style.format({col: "${:,.2f}" for col in numeric_cols}).applymap(lambda x: 'color: red;' if isinstance(x, float) and x < 0 else '', subset=['Available']))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(grouped_sof['Division'], grouped_sof['Available'], color=['green' if x >= 0 else 'red' for x in grouped_sof['Available']])
        ax.set_title('Available Funds by Division')
        ax.axhline(0, color='black', linewidth=0.8)
        st.pyplot(fig)

    # ---------------- Tab 5: Scenario Planner ----------------
    with tabs[4]:
        st.header("Scenario Planner – Non-Labor Reductions")
        contracts_reduction = st.slider("Reduce Contracts by (%)", 0, 100, 0)
        travel_reduction = st.slider("Reduce Travel by (%)", 0, 100, 0)
        training_reduction = st.slider("Reduce Training by (%)", 0, 100, 0)
        supplies_reduction = st.slider("Reduce Supplies by (%)", 0, 100, 0)
        equipment_reduction = st.slider("Reduce Equipment by (%)", 0, 100, 0)
        scenario_plan = grouped_plan.copy()
        for col, reduction in zip(['Contracts', 'Travel', 'Training', 'Supplies', 'Equip'], [contracts_reduction, travel_reduction, training_reduction, supplies_reduction, equipment_reduction]):
            if col in scenario_plan.columns:
                scenario_plan[col + ' (Adj)'] = scenario_plan[col] * (1 - reduction / 100)
        adj_expense_cols = [col + ' (Adj)' for col in ['Contracts', 'Travel', 'Training', 'Supplies', 'Equip'] if col + ' (Adj)' in scenario_plan.columns]
        scenario_plan['Adjusted Solvency'] = scenario_plan['FY TARGET $ 100%'] - (scenario_plan[['TOTAL LABOR & OH', 'Recruits Labor', 'Recruits OH', 'Recruits Lab & OH', 'OGAs', 'IDX', 'DIR-IND', 'HRPP', 'Other', 'Shop']].sum(axis=1) + scenario_plan[adj_expense_cols].sum(axis=1))
        display_cols = ['Directorate', 'Division', 'FY TARGET $ 100%'] + adj_expense_cols + ['Adjusted Solvency']
        scenario_numeric_cols = scenario_plan[display_cols].select_dtypes(include='number').columns
        st.dataframe(scenario_plan[display_cols].style.format({col: "${:,.2f}" for col in scenario_numeric_cols}))
        total_adj_solvency = scenario_plan['Adjusted Solvency'].sum()
        st.subheader(f"Total Adjusted Solvency: ${total_adj_solvency:,.2f}")

    # ---------------- Tab 6: ScenarioSolvency ----------------
    with tabs[5]:
        st.header("ScenarioSolvency – Projected Adjustments")

        # Load the Actuals-ScenarioSolvency sheet
        scenario_df = xl.parse("Actuals-ScenarioSolvency")
        scenario_df.columns = scenario_df.columns.str.strip()

        # Identify projected columns
        projected_cols = ['ProjectedContracts', 'ProjectedEquip', 'ProjectedLabor (.47)', 'ProjectedOverhead', 'ProjectedSupplies', 'ProjectedTravel']

        # Apply scenario sliders
        st.subheader("Adjust Projected Costs (%)")
        adjustments = {}
        for col in projected_cols:
            adjustments[col] = st.slider(f"Adjust {col}", -100, 100, 0)

        # Apply adjustments
        adjusted_df = scenario_df.copy()
        for col in projected_cols:
            adjustment_factor = 1 + adjustments[col] / 100
            adjusted_df[col] = adjusted_df[col] * adjustment_factor

        # Recalculate 'Total' dynamically after adjustments
        expense_cols = [
            'ASSMT/Chargebacks', 'Awards', 'Contracts', 'ProjectedContracts', 
            'Equipment', 'ProjectedEquip', 'Labor', 'ProjectedLabor (.47)',
            'VERA (Placeholder - 15people)', 'OGA', 'Other', 'Overhead',
            'ProjectedOverhead', 'Separation Costs', 'Supplies', 'ProjectedSupplies',
            'Training', 'Travel (TDY and PCS)', 'ProjectedTravel'
        ]
        adjusted_df['Total'] = (
            adjusted_df['IoBAllotment'].fillna(adjusted_df['SOF Allotment']) -
            adjusted_df[expense_cols].sum(axis=1)
        )

        # Highlight projected columns
        def highlight_projected(col):
            return ['background-color: yellow' if col.name in projected_cols else '' for _ in col]

        # Apply formatting only to numeric columns
        numeric_cols = adjusted_df.select_dtypes(include='number').columns.tolist()

        # Show the full table (mirroring Excel format)
        st.subheader("Division-Level Financials")
        st.dataframe(
            adjusted_df.style
            .format({col: "${:,.2f}" for col in numeric_cols})
            .apply(highlight_projected, axis=1)
            .applymap(lambda x: 'color: red;' if isinstance(x, float) and x < 0 else '', subset=['Total'])
        )

        # CSV export button
        csv_scenario = adjusted_df.to_csv(index=False)
        st.download_button(
            label="Download Adjusted Scenario Data as CSV",
            data=csv_scenario,
            file_name='ScenarioSolvency_Adjusted.csv',
            mime='text/csv'
        )

        # Total solvency across divisions
        total_solvency = adjusted_df['Total'].sum()
        st.subheader(f"Total Solvency Across Divisions: ${total_solvency:,.2f}")

        # Stacked bar chart for adjusted projections
        st.subheader("Adjusted Projected Costs by Division (Stacked)")
        stacked_data = adjusted_df.melt(id_vars=['Division'], value_vars=projected_cols, var_name='Category', value_name='Amount')
        fig = px.bar(stacked_data, x='Division', y='Amount', color='Category', title="Adjusted Projected Costs by Division (Stacked)")
        st.plotly_chart(fig, use_container_width=True)

        # GPT Insights (detailed)
        st.subheader("Leadership Insights")
        top_labor = adjusted_df[['Division', 'ProjectedLabor (.47)']].sort_values(by='ProjectedLabor (.47)', ascending=False).head(1)
        top_contract = adjusted_df[['Division', 'ProjectedContracts']].sort_values(by='ProjectedContracts', ascending=False).head(1)
        overall_proj = adjusted_df[projected_cols].sum()

        st.write(f"1. **{top_labor.iloc[0]['Division']} Division** holds the highest projected labor costs at **${top_labor.iloc[0]['ProjectedLabor (.47)']:,.2f}**, signaling a major workforce expenditure hotspot.")
        st.write(f"2. **{top_contract.iloc[0]['Division']} Division** has the largest projected contracts at **${top_contract.iloc[0]['ProjectedContracts']:,.2f}**, marking it as a focal point for contract strategy revisions.")
        st.write(f"3. Cumulative projections across divisions show **Labor** and **Contracts** as the top cost drivers at **${overall_proj['ProjectedLabor (.47)']:,.2f}** and **${overall_proj['ProjectedContracts']:,.2f}**, respectively, requiring focused cost-control measures.")
