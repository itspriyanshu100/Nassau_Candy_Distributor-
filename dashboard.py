import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_excel(
        "nassau_candy_analysis.xlsx",
        sheet_name=None
    )

    product_df = data["Product_Summary"]
    division_df = data["Division_Summary"]
    kpi_df = data["KPI_Data"]
    volatility_df = data["Margin_Volatility"]   # ADDED KPI DATA

    product_df.columns = product_df.columns.str.strip()
    division_df.columns = division_df.columns.str.strip()
    kpi_df.columns = kpi_df.columns.str.strip()
    volatility_df.columns = volatility_df.columns.str.strip()

    kpi_df["Order Date"] = pd.to_datetime(kpi_df["Order Date"]).dt.date
    kpi_df["Ship Date"] = pd.to_datetime(kpi_df["Ship Date"]).dt.date

    return product_df, division_df, kpi_df, volatility_df


product_df, division_df, kpi_df, volatility_df = load_data()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.title("Filters & Controls")

search_product = st.sidebar.text_input("Product Search")

division_list = ["All"] + sorted(kpi_df["Division"].dropna().unique())

selected_division = st.sidebar.selectbox(
    "Division Filter",
    division_list
)

margin_threshold = st.sidebar.slider(
    "Margin Threshold %",
    0,300,50
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(
        kpi_df["Order Date"].min(),
        kpi_df["Order Date"].max()
    )
)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------

filtered_df = kpi_df.copy()

if selected_division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == selected_division
    ]

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date) &
        (filtered_df["Order Date"] <= end_date)
    ]

# -------------------------------------------------
# PRODUCT SUMMARY
# -------------------------------------------------

filtered_product_df = filtered_df.groupby(
    "Product Name"
).agg({
    "Sales":"sum",
    "Gross Profit":"sum",
    "Units":"sum"
}).reset_index()

filtered_product_df["gross_margin_%"] = (
    filtered_product_df["Gross Profit"] /
    filtered_product_df["Sales"]
) * 100

# NEW KPI
filtered_product_df["profit_per_unit"] = (
    filtered_product_df["Gross Profit"] /
    filtered_product_df["Units"]
)

filtered_product_df = filtered_product_df[
    filtered_product_df["gross_margin_%"] >= margin_threshold
]

if search_product:

    filtered_product_df = filtered_product_df[
        filtered_product_df["Product Name"].str.contains(
            search_product,
            case=False
        )
    ]

# -------------------------------------------------
# DIVISION SUMMARY
# -------------------------------------------------

filtered_division_df = filtered_df.groupby(
    "Division"
).agg({
    "Sales":"sum",
    "Gross Profit":"sum",
    "Units":"sum"
}).reset_index()

filtered_division_df.rename(columns={
    "Sales":"total_sales",
    "Gross Profit":"total_profit"
}, inplace=True)

filtered_division_df["margin_%"] = (
    filtered_division_df["total_profit"] /
    filtered_division_df["total_sales"]
) * 100

# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()

avg_margin = 0

if total_sales != 0:
    avg_margin = (total_profit / total_sales) * 100


# NEW KPI
avg_profit_per_unit = filtered_product_df["profit_per_unit"].mean()

# calculate margin per transaction
filtered_df["margin_%"] = (
    filtered_df["Gross Profit"] / filtered_df["Sales"]
) * 100

# NEW KPI
margin_volatility = filtered_df["margin_%"].std()

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.image("logo.png", width=450)

st.title("Nassau Candy Profitability Dashboard")

st.caption(
    "Interactive Business Performance & Profitability Analytics"
)

st.markdown("---")

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric("Total Sales", f"${total_sales:,.0f}")

with kpi2:
    st.metric("Total Profit", f"${total_profit:,.0f}")

with kpi3:
    st.metric("Average Margin %", f"{avg_margin:.2f}%")

with kpi4:
    st.metric("Profit per Unit", f"${avg_profit_per_unit:.2f}")

with kpi5:
    st.metric("Margin Volatility", f"{margin_volatility:.2f}")

# -------------------------------------------------
# TABS
# -------------------------------------------------

tab1,tab2,tab3,tab4 = st.tabs([
    "📊 KPI & Product Overview",
    "📈Division Performance",
    "📝Cost vs Margin",
    "📋Profit Concentration"
])

# -------------------------------------------------
# TAB 1 : PRODUCT OVERVIEW
# -------------------------------------------------

with tab1:

    st.subheader("Top 10 Profitable Products")

    top_products = filtered_product_df.sort_values(
        "Gross Profit",
        ascending=False
    ).head(10)

    fig = px.bar(
        top_products,
        x="Product Name",
        y="Gross Profit",
        color="Gross Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profit Contribution")

    filtered_product_df["profit_contribution_%"] = (
        filtered_product_df["Gross Profit"] /
        filtered_product_df["Gross Profit"].sum()
    ) * 100

    fig2 = px.bar(
        filtered_product_df,
        x="Product Name",
        y="profit_contribution_%"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Revenue Contribution by Product")

    # Calculate revenue contribution
    filtered_product_df["revenue_contribution_%"] = (
        filtered_product_df["Sales"] /
        filtered_product_df["Sales"].sum()
    ) * 100

    rev_chart = filtered_product_df.sort_values(
        "revenue_contribution_%",
        ascending=False
    ).head(10)

    fig3 = px.bar(
        rev_chart,
        x="Product Name",
        y="revenue_contribution_%",
        color="revenue_contribution_%",
        title="Top Revenue Contributing Products"
    )

    st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------
# TAB 2 : DIVISION PERFORMANCE
# -------------------------------------------------

with tab2:

    st.subheader("Revenue vs Profit by Division")

    fig = px.bar(
        filtered_division_df,
        x="Division",
        y=["total_sales","total_profit"],
        barmode="group"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Margin Distribution by Division")

    fig2 = px.bar(
        filtered_division_df,
        x="Division",
        y="margin_%",
        color="margin_%"
    )

    st.plotly_chart(fig2,use_container_width=True)

# -------------------------------------------------
# TAB 3 : COST VS MARGIN
# -------------------------------------------------

with tab3:

    st.subheader("Sales vs Margin Analysis")

    fig = px.scatter(
    filtered_product_df,
    x="Sales",
    y="gross_margin_%",
    size="Units",
    color="gross_margin_%",
    hover_name="Product Name",
    title="Sales vs Margin Analysis"
)

# Threshold lines
    fig.add_vline(x=3000, line_dash="dash", line_color="red",
              annotation_text="High Sales Threshold")

    fig.add_hline(y=60, line_dash="dash", line_color="yellow",
              annotation_text="Healthy Margin Threshold")

# FIX AXIS RANGE
    fig.update_xaxes(range=[0, 5000])
    fig.update_yaxes(range=[40, 85])

    st.plotly_chart(fig, use_container_width=True)  


    st.subheader("Margin Risk Flags")

    risk_products = product_df[
        product_df["cost_flag"] != "normal"
    ].copy()

    st.dataframe(
        risk_products[
        ["Product Name","total_sales","total_profit","gross_margin_%","cost_flag"]
        ]
    )

# -------------------------------------------------
# TAB 4 : PROFIT CONCENTRATION
# -------------------------------------------------

with tab4:

    st.subheader("Pareto Profit Contribution")

    sorted_df = filtered_product_df.sort_values(
        "Gross Profit",
        ascending=False
    )

    sorted_df["cumulative_%"] = (
        sorted_df["Gross Profit"].cumsum() /
        sorted_df["Gross Profit"].sum()
    ) * 100

    fig = px.line(
        sorted_df,
        x="Product Name",
        y="cumulative_%"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Dependency Indicator")

    top3_profit = sorted_df.head(3)["Gross Profit"].sum()

    dependency_ratio = (
        top3_profit /
        sorted_df["Gross Profit"].sum()
    ) * 100

    st.metric(
        "Top 3 Product Profit Dependency",
        f"{dependency_ratio:.2f}%"
    )