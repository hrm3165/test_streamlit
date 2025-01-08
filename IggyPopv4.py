#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
from io import BytesIO

columns_to_keep = [
    'Collection Name', 'Product Gender', 'Activity Name',
    'SubActivityName', 'Generic Color', 'Size',
    'Cancelled', 'Shape Name', 'Material Name', 'Type Name',
    'Color Name', 'Delivery Group', 'Exotic Code', 
    'In Look', "Key Account Name", "Group-Non Group",
    "Store Market", "Mgm Zone Name", "Store Region",
    "QTY", "FRV", "SKU", 
    "Life Type Code"
]

st.title("IggyPop")

st.sidebar.title("CHOOSE ACTION")
action = st.sidebar.radio(
    "CHOOSE ACTION",  
    ["Filter Mandatory Columns", "Concat Two Files", "Update Codification"]  
)

st.write(f"Action : {action}")

if action == "Filter Mandatory Columns":
    st.header("Filter Mandatory Columns")
    
    uploaded_file = st.file_uploader("Upload your file", type=["xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("File Loaded.")
            
            missing_columns = [col for col in columns_to_keep if col not in df.columns]
            if missing_columns:
                st.warning(f"Missing Columns : {missing_columns}")
                st.stop()
            else:
                df_cleaned = df[columns_to_keep].copy()
                st.success("Mandatory Columns filtered.")
                st.dataframe(df_cleaned.head())
            
                try:
                    output = BytesIO()
                    df_cleaned.to_excel(output, index=False, sheet_name='Sheet1')
                    output.seek(0) 
                    
                    file_name = st.text_input("Input file name (with .xlsx) & press enter", "filtered_file.xlsx")

                    if file_name:
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name="filtered_file.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error : {e}")
        
        except Exception as e:
            st.error(f"Error : {e}")

elif action == "Concat Two Files":
    st.header("Concat Two Files")
    
    uploaded_file1 = st.file_uploader("Upload first file", type=["xlsx"], key="file1")
    uploaded_file2 = st.file_uploader("Upload second file", type=["xlsx"], key="file2")
    
    if uploaded_file1 and uploaded_file2:
        try:
            df1 = pd.read_excel(uploaded_file1)
            df2 = pd.read_excel(uploaded_file2)
            
            missing_columns_df1 = [col for col in columns_to_keep if col not in df1.columns]
            missing_columns_df2 = [col for col in columns_to_keep if col not in df2.columns]
            
            if missing_columns_df1:
                st.warning(f"Missing Columns in file 1 : {missing_columns_df1}")
            elif missing_columns_df2:
                st.warning(f"Missing Columns in file 2 : {missing_columns_df2}")
            else:

                df1_cleaned = df1[columns_to_keep].copy()
                df2_cleaned = df2[columns_to_keep].copy()
                concatenated_df = pd.concat([df1_cleaned, df2_cleaned], ignore_index=True)
                
                concatenated_df = concatenated_df.drop_duplicates()
                
                st.success("Files have been concatened.")
                st.dataframe(concatenated_df.head())
                
                try:
                    output = BytesIO()
                    concatenated_df.to_excel(output, index=False, sheet_name='Sheet1')
                    output.seek(0) 
                
                    file_name = st.text_input("Input file name (with .xlsx) & press enter", "modified_file.xlsx")
    
                    if file_name:
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name="filtered_file.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                except Exception as e:
                    st.error(f"Error : {e}")
                    
        except Exception as e:
            st.error(f"Error : {e}")

elif action == "Update Codification":
    st.header("Update Codification")
    

    data_file = st.file_uploader("Upload your data file", type=["xlsx"], key="data_file")
    
    separator = st.radio(
        "Select separator for mapping",
        ("Comma (,)", "Tabulation (\\t)"),
        index=0
    )
    
    st.subheader("Define mapping")
    mapping_input = st.text_area(
        "Enter mapping without header: 'Old_GNE,New_GNE' or 'Old_GNE\tNew_GNE'",
        placeholder="Example:\nABC123,XYZ456\nDEF789,GHI012"
    )
    
    if data_file and mapping_input:
        try:
            df = pd.read_excel(data_file)
            
            delimiter = ',' if separator == "Comma (,)" else '\t'
            
            mapping_lines = mapping_input.strip().split("\n")
            mapping_dict = {}
            for line in mapping_lines:
                parts = line.split(delimiter)
                if len(parts) == 2:
                    old_ref, new_ref = parts
                    mapping_dict[old_ref.strip()] = new_ref.strip()
                else:
                    st.warning(f"Line ignored, check format : {line}")
            
            if 'Generic Color' in df.columns:

                missing_refs = [ref for ref in mapping_dict.keys() if ref not in df['Generic Color'].values]
                
                if missing_refs:
                    st.warning(
                        f"References not found in file :\n"
                        f"{', '.join(missing_refs)}"
                    )
                
                # Appliquer le mapping
                original_df = df.copy()
                df['Generic Color'] = df['Generic Color'].replace(mapping_dict)

                modified_rows = df[df['Generic Color'] != original_df['Generic Color']]
                
                if not modified_rows.empty:
                    st.success(f"{len(modified_rows)} lignes have been modified.")
                    st.dataframe(modified_rows)
                else:
                    st.info("No line modified.")
                
                try:
                    output = BytesIO()
                    df.to_excel(output, index=False, sheet_name='Sheet1')
                    output.seek(0)
                    
                    file_name = st.text_input("Input file name (with .xlsx) & press enter", "modified_file.xlsx")
                    
                    if file_name:
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.download_button(
                            label="Download",
                            data=output,
                            file_name="filtered_file.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                except Exception as e:
                    st.error(f"Error : {e}")
            else:
                st.warning("'Generic Color' is not a column in file uploaded.")
        except Exception as e:
            st.error(f"Error while updating : {e}")


