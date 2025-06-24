import streamlit as st
import pandas as pd
import io
from io import BytesIO

st.set_page_config(page_title="CSV Merger", layout="centered")
st.title("📁 Combine Multiple CSV Files with Matching Headers")

uploaded_files = st.file_uploader(
    "Upload CSV files", type=["csv"], accept_multiple_files=True
)

if uploaded_files:
    dfs = []
    column_names = None
    errors = []

    def read_csv_with_forced_header(file, header=None):
        raw = file.read()
        text = raw.decode("utf-8-sig", errors="ignore").replace("\r", "\n")
        file.seek(0)
        df = pd.read_csv(io.StringIO(text), header=None)
        if header:
            df.columns = header
            df = df[1:]  # Drop the row that was originally a header
        return df

    for i, file in enumerate(uploaded_files):
        try:
            if i == 0:
                raw = file.read()
                text = raw.decode("utf-8-sig", errors="ignore").replace("\r", "\n")
                file.seek(0)
                preview = pd.read_csv(io.StringIO(text), header=None)
                column_names = preview.iloc[0].tolist()
                df = preview[1:].copy()
                df.columns = column_names
            else:
                df = read_csv_with_forced_header(file, column_names)
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
