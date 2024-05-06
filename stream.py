import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Superstore", page_icon=":bar_chart:", layout="wide")
st.title(" \U0001F4CA Sample Superstore EDA")
st.markdown(',<style>div.block-container{padding-top:1rem;},</style>',unsafe_allow_html=True)

f1 = st.file_uploader(':file_folder:upload a file',type=(["csv","xlsx"]))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
     
    df = pd.read_csv("Global_Superstore_lite.csv", encoding="ISO-8859-1" )  

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"]) 

# min max dates
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("end Date", endDate))

df = df[(df["Order Date"]>=date1) & (df["Order Date"] <=date2)].copy()

st.sidebar.header("choose your filter: ")
#creating the region
Region = st.sidebar.multiselect("pick Region", df["Region"].unique())
if not Region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(Region)]

#create for state
State = st.sidebar.multiselect("pick state", df2["State"].unique())
if not State:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(State)] 

#create for city
City = st.sidebar.multiselect("pick city",df3["City"].unique())

if not Region and not State and not City:
    filtered_df = df
elif not State and not City:
    filtered_df = df[df["Region"].isin(Region)]
elif not Region and not City:
     filtered_df =  df3[df["Region"].isin(State) & df3["City"].isin(City)]
elif not Region and not State:
    filtered_df =  df3[df["Region"].isin(State) & df3["State"].isin(City)] 
elif City:
    filtered_df = df3[df3["City"].isin(City)]  
else:
    filtered_df = df3[df3["Region"].isin(Region) & df3["State"].isin(State)& df3 ["City"]]
if not City:
    df4 = df3.copy()
else:
    df4 = df3[df3["City"].isin(City)]

# Create for antecedents and descendants
SubCategory = st.sidebar.multiselect("Pick Sub-Category (Antecedents)", df4["Sub-Category"].unique())
SubCategoryDesc = st.sidebar.multiselect("Pick Sub-Category (Descendants)", df4["Sub-Category"].unique())
if not SubCategory and not SubCategoryDesc:
    filtered_df = df4.copy()
elif not SubCategoryDesc:
    filtered_df = df4[df4["Sub-Category"].isin(SubCategory)]
elif not SubCategory:
    filtered_df = df4[df4["Sub-Category"].isin(SubCategoryDesc)]
else:
    filtered_df = df4[(df4["Sub-Category"].isin(SubCategory)) | (df4["Sub-Category"].isin(SubCategoryDesc))]

st.write(filtered_df.head())

Category_df = filtered_df.groupby(by =["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise sales")
    bar_fig = px.bar(Category_df, x="Category", y="Sales", text=[f'${x:,.2f}' for x in Category_df["Sales"]],
              template="seaborn")
    st.plotly_chart(bar_fig)

with col2:
    st.subheader("Region wise sales")
    pie_fig = px.pie(filtered_df, values="Sales", names="Region")
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(pie_fig, use_container_width=True)

with col1:
    st.subheader("Sales Heatmap")
    heatmap_fig = px.imshow(filtered_df.pivot_table(index='Category', columns='Sub-Category', values='Sales', aggfunc='sum'), 
                            labels=dict(x="Sub-Category", y="Category", color="Sales"),
                            title="Sales Heatmap")
    st.plotly_chart(heatmap_fig)




cl1, cl2 = st.columns(2)
with cl1:
 with st.expander("category_view Data"):
     st.write(Category_df.style.background_gradient(cmap= "Blues"))
     csv = Category_df.to_csv(index = False).encode('utf-8')
     st.download_button("download data", data = csv, file_name="Category csv", mime="text/csv",
                        help = "click here to download the data as csv file")

with cl2:
 with st.expander("Region_view Data"):
     Region = filtered_df.groupby(by ="Region", as_index = False)["Sales"].sum()
     st.write(Category_df.style.background_gradient(cmap= "Oranges"))
     csv = Region.to_csv(index = False).encode('utf-8')
     st.download_button("download data", data = csv, file_name="Region csv", mime="text/csv",
                        help = "click here to download the data as csv file")




filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time series analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("Y: %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales":"Amount"},height = 500, width = 1000, template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View data of time series:"):
    st.write(linechart.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download data', data=csv, file_name="Time series.csv", mime="text/csv")


#map based on segment, category,sub-category
st.subheader("Hierachial veiw of sales")
fig3 = px.treemap(filtered_df, path = ["Segment","Category","Sub-Category"],values = "Sales",hover_data = ["Sales"],
                                     color="Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3,use_container_width=True)

#segment category sales
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("segment wise sales")
    fig = px.pie(filtered_df, values="Sales",names="Segment",template="plotly_dark")
    fig.update_traces(text = filtered_df["Segment"],textposition="inside")
    st.plotly_chart(fig,use_container_width = True)
with chart1:
    st.subheader(" wise sales")
    fig = px.pie(filtered_df, values="Sales",names="Category",template="plotly_dark")
    fig.update_traces(text = filtered_df["Category"],textposition="inside")
    st.plotly_chart(fig,use_container_width = True)

import plotly.figure_factory as ff
st.subheader("month wise subchategory sales summary")
with st.markdown("month wise sub category"):
     filtered_df["month"] = filtered_df["Order Date"].dt.strftime("%b") 
     sub_Category_year = pd.pivot_table(data = filtered_df, values="Sales", index = ["Sub-Category"],columns="month")
     st.write(sub_Category_year.style.background_gradient(cmap="Blues"))

#scatter
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
layout = {'title': "sales Vs profit"}
data1.update_layout(layout)
st.plotly_chart(data1, use_container_width=True)
