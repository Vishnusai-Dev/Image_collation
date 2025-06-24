import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CSV & Excel Merger", layout="centered")

st.title("📁 Combine Multiple CSV or Excel Files")

# 1. File Uploader FIRST
uploaded_files = st.file_uploader(
    "Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True
)

if uploaded_files:  # Check if any files were uploaded
    dfs = []
    all_columns = set()
    errors = []

    # Step 1: Collect all columns
    for file in uploaded_files:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                continue
            if df.empty:
                errors.append(f"{file.name} is empty. Skipping.")
                continue
            all_columns.update(df.columns)
        except Exception as e:
            errors.append(f"❌ Failed reading {file.name}: {e}")

    # Step 2: Align columns and append
    for file in uploaded_files:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                continue
            if df.empty:
                continue
            df = df.reindex(columns=all_columns)
            dfs.append(df)
        except Exception as e:
            errors.append(f"❌ Skipped {file.name} due to error: {e}")

    # Step 3: Combine and show results
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        st.success("✅ Files combined successfully!")
        st.write(combined_df)

        def convert_df(df):
            output = BytesIO()
            df.to_csv(output, index=False)
            return output.getvalue()

        csv_data = convert_df(combined_df)
        st.download_button("📥 Download Combined File", csv_data, "combined_output.csv", "text/csv")
    else:
        st.error("No valid files to merge.")

    # Step 4: Show errors if any
    if errors:
        st.warning("Some files could not be processed:")
        for err in errors:
            st.text(err)
else:
    st.info("⬆️ Upload at least one file to begin.")
