import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CSV Merger", layout="wide")
st.title("📁 Merge Multiple CSV Files (with Different Headers)")

uploaded_files = st.file_uploader(
    "Upload multiple CSV files", type="csv", accept_multiple_files=True
)

if uploaded_files:
    all_dfs = []
    all_columns = set()

    for file in uploaded_files:
        try:
            # Read CSV with safe defaults
            df = pd.read_csv(file, header=0, dtype=str)

            # Clean up headers
            df.columns = [str(col).strip() for col in df.columns]
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Remove index columns if any

            all_dfs.append(df)
            all_columns.update(df.columns)
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    if all_dfs:
        # Create unified column list
        all_columns = sorted(all_columns)
        merged_df = pd.DataFrame(columns=all_columns)

        # Reindex each file to match merged columns
        for df in all_dfs:
            df_reindexed = df.reindex(columns=all_columns, fill_value="")
            merged_df = pd.concat([merged_df, df_reindexed], ignore_index=True)

        st.success(f"✅ Merged {len(uploaded_files)} files with {len(all_columns)} total columns.")
        st.dataframe(merged_df.head(100), use_container_width=True)

        # Prepare download
        csv_buffer = io.StringIO()
        merged_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Download Merged CSV",
            data=csv_buffer.getvalue(),
            file_name="merged_output.csv",
            mime="text/csv"
        )
    else:
        st.warning("No valid files to process.")
else:
    st.info("Please upload two or more CSV files to begin merging.")
