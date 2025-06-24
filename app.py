import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="CSV Merger", layout="wide")
st.title("📁 Merge Multiple CSV Files with Varying Headers")

uploaded_files = st.file_uploader(
    "Upload multiple CSV files", type="csv", accept_multiple_files=True
)

if uploaded_files:
    all_dfs = []
    all_columns = set()

    # Read all files and collect headers
    for file in uploaded_files:
        df = pd.read_csv(file)
        all_dfs.append(df)
        all_columns.update(df.columns)

    # Rebuild all DataFrames to have all headers
    all_columns = sorted(all_columns)
    merged_df = pd.DataFrame(columns=all_columns)

    for df in all_dfs:
        df_reindexed = df.reindex(columns=all_columns, fill_value="")
        merged_df = pd.concat([merged_df, df_reindexed], ignore_index=True)

    st.success(f"✅ Merged {len(uploaded_files)} files successfully!")
    st.dataframe(merged_df.head(100), use_container_width=True)

    # Provide download button
    csv_buffer = io.StringIO()
    merged_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Merged CSV",
        data=csv_buffer.getvalue(),
        file_name="merged_output.csv",
        mime="text/csv"
    )
else:
    st.info("Upload at least 2 CSV files to begin merging.")

