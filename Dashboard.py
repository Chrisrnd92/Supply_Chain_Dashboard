# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

#setting up the page
st.set_page_config(page_title= "Dashboard", layout="wide")
st.title("Product Supply Chain Dashboard")

@st.cache_data
def load_data():
    df1 = pd.read_csv("Log_Data.csv")
    df2 = pd.read_csv("Products.csv")
    return df1, df2

df1, df2 = load_data()
df = df1.merge(df2[['Product_ID','Name','Gender']], on='Product_ID', how='left')

#replace Names in the column Source Factory
df.columns = df.columns.str.strip()
df["Product Name"] = df["Name"].apply(lambda x: x.split(' ', 1)[1] if ' ' in x else x)

df["No. of Pieces Sold"]= df["No. of pieces sold"]
df["Source Factory"]= df["Source Factory"].replace({'F001':'Factory 1', 
                                                    'F002':'Factory 2',
                                                    'F003':'Factory 3',
                                                    'F004':'Factory 4',
                                                    'F005':'Factory 5'})
df["Gender"]= df["Gender"].replace({'M':'Male', 'F':'Female', 'U':'Unisex'})

st.header("Sample")
st.sidebar.header("Filters")

#Display Product Analysis using Streamlit
Product_Analysis = (
               df.groupby(["Product Name", "Gender"])[["No. of Pieces Sold", "No. of Pieces Returned"]].sum().reset_index()
               )
fig_Product_Analysis = px.pie(Product_Analysis, names='Product Name', values='No. of Pieces Sold', title='Net Product Sold by Product Type')
col1, col2 = st.columns(2)
col1.dataframe(Product_Analysis)
col2.plotly_chart(fig_Product_Analysis, use_container_width=True)


# adding filters for Factory, Warehouse, Product
# filter by Factory
selected_Factory = st.sidebar.multiselect("Select Factory:", df["Source Factory"].unique(), default=df["Source Factory"].unique())
# filter by Warehouse
selected_Warehouse = st.sidebar.multiselect("Select Warehouse:", df["Dest. Warehouse"].unique(), default=df["Dest. Warehouse"].unique())
# filter by gender
selected_Gender = st.sidebar.multiselect("Select Gender:", df["Gender"].unique(), default=df["Gender"].unique())
# filter by Product
selected_Product = st.sidebar.multiselect("Select Product:", df["Product Name"].unique(), default=df["Product Name"].unique())


boolean_filter = (
                 df["Source Factory"].isin(selected_Factory) & 
                 df["Dest. Warehouse"].isin(selected_Warehouse) &
                 df["Product Name"].isin(selected_Product) &
                 df["Gender"].isin(selected_Gender)
                 )
filtered = df.loc[boolean_filter]

# Calculate metrics using pandas
num_Orders = len(filtered)
manufactured_pieces = filtered["Total No. of Pieces"].sum()
avg_sold_pieces = filtered["No. of Pieces Sold"].mean()
avg_pieces_returned = filtered["No. of Pieces Returned"].mean()


#Display Metrics using Streamlit
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Number of Orders", value=f"{num_Orders:,}")
col2.metric(label="Manufactured Pieces", value=f"{manufactured_pieces:,.0f}")
col3.metric(label="Avg. Sold Pieces", value=f"{avg_sold_pieces:.2f}")
col4.metric(label="Avg. Returned Pieces", value=f"{avg_pieces_returned:,.0f}")

avg_returnedproducts = (
               filtered.groupby("Source Factory")["No. of Pieces Returned"].mean().reset_index()
               )
rate_returnedproducts = (
               filtered.groupby(["Source Factory","Gender"])[["No. of Pieces Returned", "No. of Pieces Sold"]].sum().reset_index()
               )
rate_returnedproducts["Return Rate (%)"] = (rate_returnedproducts["No. of Pieces Returned"] / rate_returnedproducts["No. of Pieces Sold"]
) * 100

fig_avg_returned_product = px.bar(avg_returnedproducts, x="Source Factory",y="No. of Pieces Returned", title="Avg. Pieces Returned", labels={"No. of Pieces Returned":"No. of Pieces Returned per Factory"},
    color_discrete_sequence=px.colors.qualitative.Prism)
st.plotly_chart(fig_avg_returned_product, use_container_width=True)
fig_rate_returnedproduct = px.bar(rate_returnedproducts, x="Source Factory",y="Return Rate (%)", color="Gender", title="Return Rate (%)", labels={"Return Rate (%)":"No. of Pieces Returned per Factory"},
    color_discrete_sequence=px.colors.qualitative.Prism)
st.plotly_chart(fig_rate_returnedproduct, use_container_width=True)

st.header("Male vs Female Product Returns Statistics")
df["Date"] = pd.to_datetime(df["Date"])
# Group by Date and Gender
returns_over_time = (
    df.groupby(["Date", "Gender"])["No. of Pieces Returned"]
    .sum()
    .reset_index()
)
returns_over_time_filtered_gender = returns_over_time[returns_over_time["Gender"].isin(["Male", "Female"])]

fig1 = px.line(data_frame=returns_over_time_filtered_gender, 
              x='Date', 
              y='No. of Pieces Returned', 
              title='No. of Pieces Returned over Time',
              color='Gender',
              markers=False, # make the markers visible on the line plot
              color_discrete_sequence=px.colors.qualitative.Set2,
              labels={'Date':' ', 'value':'No. of Pieces Returned', 'variable':'Gender'},
              )

fig1.update_traces(
    line=dict(dash='solid', width=1.5)  # Dashed lines with width 4 and purple color
)

st.plotly_chart(fig1, use_container_width=True)








st.header("Raw Data")
st.dataframe(df)
