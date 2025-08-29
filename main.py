import streamlit as st 
import pandas as pd 
import os 
import google.genai as genai

st.title("Excel Compare Utility")
st.set_page_config(layout="wide")

file1 = st.file_uploader("Excel 1", type=["xlsx"])
file2 = st.file_uploader("Excel 2", type=["xlsx"])

if file1 is not None and file2 is not None:

    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # st.write(df1)

    print(df1.columns)
    print(df2.columns)

    if df1 is not None and df2 is not None:
        st.success("Both files uploaded successfully")

        common_columns = list(set(df1.columns).intersection(set(df2.columns)))
        join_keys = st.multiselect("Pick join keys", common_columns)

        clicked = st.button("Generate Row/Column level changes")

        if clicked: 
            if not join_keys:
                st.error("Please pick atleast one join key")
            
            else:
                col1, col2 = st.columns([6,2])
                merged_df = df1.merge(df2, on=join_keys, how="outer",suffixes=("_x", "_y"), indicator=True)
                # st.write(merged_df)

                # Deleted rows
                deleted_rows = merged_df[merged_df["_merge"] == "left_only"]
                col1.write("Deleted Rows")
                df1_old_cols = [col for col in deleted_rows.columns if col.endswith("_x") or col in join_keys]
                deleted_rows = deleted_rows[df1_old_cols]
                deleted_rows = deleted_rows.rename(columns={col: col.replace("_x","") for col in deleted_rows.columns})
                col1.write(deleted_rows)

                delete_count = len(deleted_rows)
                col2.metric("Rows deleted: ", delete_count)

                # Added rows
                col1, col2 = st.columns([6,2])
                added_rows = merged_df[merged_df["_merge"] == "right_only"]
                col1.write("Added rows")
                df2_old_cols = [col for col in added_rows.columns if col.endswith("_y") or col in join_keys]
                added_rows = added_rows[df2_old_cols]
                added_rows = added_rows.rename(columns={col: col.replace("_y","") for col in added_rows.columns})
                col1.write(added_rows)

                add_count = len(added_rows)
                col2.metric("Rows added: ", add_count)


                #Column level changes
                col1, col2 = st.columns([6,2])
                changed = []
                common = merged_df[merged_df["_merge"] == "both"]

                non_key_cols = [col for col in df1.columns if col not in join_keys]


                for col in non_key_cols:
                    old_col = col + "_x"
                    new_col = col + "_y"

                    diff = common[common[old_col] != common[new_col]]

                    if not diff.empty:
                        temp = diff[join_keys + [old_col, new_col]].copy()
                        temp["ChangedColumn"] = col 
                        temp = temp.rename(columns={old_col: "OldValue", new_col: "NewValue"})
                        changed.append(temp) 
                

                if changed:
                    changed = pd.concat(changed, ignore_index=True)
                    col1.write("Column level changes")
                    col1.write(changed)

                    changed_count = len(changed)
                    col2.metric("Columns changed: ", changed_count)

                    col_change_counts = changed["ChangedColumn"].value_counts()
                    most_changed_column = col_change_counts.idxmax()
                    most_changed_count = col_change_counts.max()

                    col2.metric("Most Changed Column", f"{most_changed_column} ({most_changed_count} changes)")
                else:
                    changed= pd.DataFrame(columns=join_keys + ["ChangedColumn","OldValue", "NewValue"])
                
        
















