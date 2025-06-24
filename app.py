
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CSV & Excel Merger", layout="centered")

st.title("📁 Combine Multiple CSV or Excel Files")

uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    dfs = []
    all_columns = set()

    # First pass: gather all unique columns
    for file in uploaded_files:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            continue
        all_columns.update(df.columns)

    all_columns = list(all_columns)

    # Second pass: align and collect data
    for file in uploaded_files:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            continue
        df = df.reindex(columns=all_columns)
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)

    st.success("✅ Files combined successfully!")
    st.write(combined_df)

    def convert_df(df):
        output = BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()

    csv_data = convert_df(combined_df)
    st.download_button("📥 Download Combined File", csv_data, "combined_output.csv", "text/csv")
