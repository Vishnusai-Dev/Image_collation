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
    column_names = None
    errors = []

    def normalize_csv(file):
        raw = file.read()
        decoded = raw.decode("utf-8-sig", errors="ignore").replace("\r", "\n")
        file.seek(0)
        return decoded

    for i, file in enumerate(uploaded_files):
        try:
            if file.name.endswith(".csv"):
                decoded = normalize_csv(file)
                if i == 0:
                    df = pd.read_csv(io.StringIO(decoded), header=0)
                    column_names = df.columns.tolist()
                    st.write(f"✅ `{file.name}` columns detected:", column_names)
                else:
                    df = pd.read_csv(io.StringIO(decoded), names=column_names, skiprows=1)
            elif file.name.endswith(".xlsx"):
                if i == 0:
                    df = pd.read_excel(file, header=0)
                    column_names = df.columns.tolist()
                    st.write(f"✅ `{file.name}` columns detected:", column_names)
                else:
                    df = pd.read_excel(file, names=column_names, skiprows=1)

            if df.empty:
                errors.append(f"{file.name} is empty. Skipping.")
                continue

            dfs.append(df)

        except Exception as e:
            errors.append(f"❌ Error reading {file.name}: {e}")

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
