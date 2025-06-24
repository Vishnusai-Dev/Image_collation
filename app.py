
import streamlit as st
import pandas as pd
import io
from io import BytesIO

st.set_page_config(page_title="CSV & Excel Merger", layout="centered")

st.title("📁 Combine Multiple CSV or Excel Files")

uploaded_files = st.file_uploader(
    "Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True
)

if uploaded_files:
    dfs = []
    all_columns = set()
    errors = []

    def safe_read(file):
        try:
            if file.name.endswith(".csv"):
                raw = file.read()
                decoded = raw.decode("utf-8", errors="ignore").replace("\r", "\n")
                file.seek(0)
                return pd.read_csv(io.StringIO(decoded))
            elif file.name.endswith(".xlsx"):
                return pd.read_excel(file)
        except Exception as e:
            raise ValueError(f"{file.name} is unreadable: {e}")

    # Step 1: Discover all columns
    for file in uploaded_files:
        try:
            df = safe_read(file)
            if df.empty:
                errors.append(f"{file.name} is empty. Skipping.")
                continue
            all_columns.update(df.columns)
        except Exception as e:
            errors.append(f"❌ Failed reading {file.name}: {e}")

    # Step 2: Align and merge
    for file in uploaded_files:
        try:
            df = safe_read(file)
            if df.empty:
                continue
            df = df.reindex(columns=all_columns)
            dfs.append(df)
        except Exception as e:
            errors.append(f"❌ Skipped {file.name} due to error: {e}")

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

    if errors:
        st.warning("Some files could not be processed:")
        for err in errors:
            st.text(err)
else:
    st.info("⬆️ Upload at least one file to begin.")
