# Full Streamlit Sales Dashboard

## Install Required Libraries


# Save this as `app.py`
import streamlit as st
import pandas as pd
import plotly.express as px
import re

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title='Sales Dashboard',
    layout='wide'
)

# -------------------------------------------------
# COLORS
# -------------------------------------------------

DARK_GREEN = '#007A33'
RED = '#E41E26'
CREAM = '#FFF8E7'
BLACK = '#1C1C1C'

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title('📊 Sales Dashboard')
st.markdown('### Category Wise | Customer Wise | Watt Wise Analysis')

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data

def load_data():
    df = pd.read_csv(
        'dataset(in).csv',
        encoding='latin1',
        low_memory=False
    )

    # ---------------- REQUIRED COLUMNS ----------------
    required_cols = [
        'ItemCategoryCode',
        'Amount',
        'Quantity',
        'Description',
        'BilltoCustomerNo'
    ]

    df = df[required_cols].copy()

    # ---------------- CLEAN DATA ----------------
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')

    df = df.dropna(subset=['ItemCategoryCode'])

    # -------------------------------------------------
    # EXTRACT WATT VALUES
    # -------------------------------------------------

    def extract_watt(text):
        if pd.isna(text):
            return None

        match = re.search(r'(\d+)\s?W', str(text).upper())

        if match:
            return match.group(1) + 'W'

        return 'Other'

    df['Watt'] = df['Description'].apply(extract_watt)

    return df


# -------------------------------------------------
# LOAD DATAFRAME
# -------------------------------------------------

df = load_data()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header('🔍 Filters')

# Category Filter
category_filter = st.sidebar.multiselect(
    'Select Category',
    options=sorted(df['ItemCategoryCode'].dropna().unique()),
    default=sorted(df['ItemCategoryCode'].dropna().unique())
)

# Watt Filter
watt_filter = st.sidebar.multiselect(
    'Select Watt',
    options=sorted(df['Watt'].dropna().unique()),
    default=sorted(df['Watt'].dropna().unique())
)

# Customer Filter
customer_filter = st.sidebar.multiselect(
    'Select Customer',
    options=sorted(df['BilltoCustomerNo'].dropna().astype(str).unique()),
    default=sorted(df['BilltoCustomerNo'].dropna().astype(str).unique())[:50]
)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------

filtered_df = df[
    (df['ItemCategoryCode'].isin(category_filter)) &
    (df['Watt'].isin(watt_filter)) &
    (df['BilltoCustomerNo'].astype(str).isin(customer_filter))
]

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

st.markdown('## 📌 Key Metrics')

# Metrics

total_revenue = filtered_df['Amount'].sum()
total_quantity = filtered_df['Quantity'].sum()
total_customers = filtered_df['BilltoCustomerNo'].nunique()
total_categories = filtered_df['ItemCategoryCode'].nunique()

# Convert Revenue to Crores
revenue_cr = total_revenue / 10000000

# KPI Columns

col1, col2, col3, col4 = st.columns(4)

col1.metric('Total Revenue', f'₹ {revenue_cr:.2f} Cr')
col2.metric('Total Quantity', f'{total_quantity:,.0f}')
col3.metric('Customers', f'{total_customers:,}')
col4.metric('Categories', f'{total_categories:,}')

# -------------------------------------------------
# CATEGORY WISE ANALYSIS
# -------------------------------------------------

st.markdown('---')
st.markdown('# 📦 Category Wise Analysis')

category_summary = (
    filtered_df.groupby('ItemCategoryCode', as_index=False)
    .agg({
        'Amount': 'sum',
        'Quantity': 'sum'
    })
)

category_summary['Revenue_Cr'] = (
    category_summary['Amount'] / 10000000
)

category_summary = category_summary.sort_values(
    by='Revenue_Cr',
    ascending=False
)

# ---------------- CHART COLUMNS ----------------

col1, col2 = st.columns(2)

# -------------------------------------------------
# CATEGORY BAR CHART
# -------------------------------------------------

with col1:

    fig1 = px.bar(
        category_summary.head(10),
        x='ItemCategoryCode',
        y='Revenue_Cr',
        text='Revenue_Cr',
        title='Top Categories by Revenue'
    )

    # ---------- BAR STYLE ----------
    fig1.update_traces(

        # OSWAL Green
        marker_color='#008037',

        texttemplate='%{text:.2f} Cr',
        textposition='outside',

        textfont=dict(
            color='black',
            size=12
        )
    )

    # ---------- LAYOUT ----------
    fig1.update_layout(

        # Background
        plot_bgcolor='white',
        paper_bgcolor='white',

        # Title
        title={
            'text': '<b>Top Categories by Revenue</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(
                size=22,
                color='#0E0E0E'
            )
        },

        # Overall Font
        font=dict(
            color='black',
            size=13
        ),

        # Size
        height=550,

        # ---------- X AXIS ----------
        xaxis=dict(

            title='Item Category',

            title_font=dict(
                color='#0B3C5D',   # Dark Blue
                size=16
            ),

            tickfont=dict(
                color='#0B3C5D',
                size=13
            ),

            showline=True,
            linewidth=2,
            linecolor='#0B3C5D',

            showgrid=False
        ),

        # ---------- Y AXIS ----------
        yaxis=dict(

            title='Revenue (Cr)',

            title_font=dict(
                color='#0B3C5D',
                size=16
            ),

            tickfont=dict(
                color='#0B3C5D',
                size=13
            ),

            showline=True,
            linewidth=2,
            linecolor='#0B3C5D',

            showgrid=False
        ),

        margin=dict(
            l=40,
            r=20,
            t=70,
            b=40
        )
    )

    st.plotly_chart(fig1, width='stretch')


  # ---------- FIG 2 : DONUT CHART ----------

fig2 = px.pie(

    top_products,

    names='ItemCategoryCode',
    values='Quantity_Lakh',

    hole=0.55,

    title='Category Contribution by Quantity Sold'
)

# ---------- Styling ----------
fig2.update_traces(

    textposition='outside',

    textinfo='percent+label',

    textfont=dict(
        size=13,
        color='black'
    ),

    marker=dict(
        line=dict(
            color='white',
            width=2
        )
    ),

    hovertemplate=
    '<b>Category:</b> %{label}<br>' +
    '<b>Quantity:</b> %{value:.2f} L<br>' +
    '<b>Contribution:</b> %{percent}<br>' +
    '<extra></extra>'
)

# ---------- Layout ----------
fig2.update_layout(

    # Background
    paper_bgcolor=cream,
    plot_bgcolor=cream,

    # ---------- TITLE ----------
    title=dict(
        text='Top Category Contribution',
        x=0.5,

        font=dict(
            size=24,
            color='black',
            family='Arial Black'
        )
    ),

    # ---------- Legend ----------
    legend=dict(

        title='Categories',

        title_font=dict(
            color=blue,
            size=15
        ),

        font=dict(
            color=blue,
            size=12
        )
    ),

    # ---------- Overall Font ----------
    font=dict(
        family='Arial',
        color='black'
    ),

    # Size
    height=650,
    width=850,

    margin=dict(
        l=40,
        r=40,
        t=90,
        b=40
    )
)

# ---------- Show ----------
st.plotly_chart(fig2, width='stretch')

# -------------------------------------------------
# CATEGORY TREEMAP
# -------------------------------------------------

fig3 = px.treemap(
    category_summary.head(15),
    path=['ItemCategoryCode'],
    values='Revenue_Cr',
    color='Revenue_Cr',
    title='Category Wise Revenue Treemap'
)

fig3.update_layout(
    height=600
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------
# CUSTOMER WISE ANALYSIS
# -------------------------------------------------

st.markdown('---')
st.markdown('# 👥 Customer Wise Analysis')

customer_summary = (
    filtered_df.groupby('BilltoCustomerNo', as_index=False)
    ['Amount']
    .sum()
)

customer_summary['Revenue_Cr'] = (
    customer_summary['Amount'] / 10000000
)

customer_summary = customer_summary.sort_values(
    by='Revenue_Cr',
    ascending=False
)

fig4 = px.bar(

    customer_summary.head(10),

    x='BilltoCustomerNo',
    y='Revenue_Cr',

    text='Revenue_Cr',

    title='👤 Top 10 Customers by Revenue'
)

# ---------- Styling ----------
fig4.update_traces(

    # OSWAL GREEN
    marker=dict(
        color='#007A33',

        line=dict(
            width=2,
            color='white'
        )
    ),

    texttemplate='₹ %{text:.2f} Cr',

    textposition='outside',

    # ---------- VALUE LABELS ----------
    textfont=dict(
        color='#1565C0',
        size=13,
        family='Arial Black'
    ),

    # ---------- HOVER ----------
    hovertemplate=
    '<b>Customer:</b> %{x}<br>' +
    '<b>Revenue:</b> ₹ %{y:.2f} Cr<br>' +
    '<extra></extra>'
)

# ---------- Layout ----------
fig4.update_layout(

    # Background
    plot_bgcolor='#FFF8E7',
    paper_bgcolor='#FFF8E7',

    # ---------- TITLE ----------
    title=dict(

        x=0.5,

        font=dict(
            size=24,
            color='#007A33',
            family='Arial Black'
        )
    ),

    # ---------- X AXIS ----------
    xaxis=dict(

        title='Customer Number',

        title_font=dict(
            color='black',
            size=16,
            family='Arial Black'
        ),

        tickfont=dict(
            color='black',
            size=12
        ),

        showline=True,
        linewidth=2,
        linecolor='#1565C0',

        showgrid=False
    ),

    # ---------- Y AXIS ----------
    yaxis=dict(

        title='Revenue (Cr)',

        title_font=dict(
            color='black',
            size=16,
            family='Arial Black'
        ),

        tickfont=dict(
            color='black',
            size=12
        ),

        showline=True,
        linewidth=2,
        linecolor='#1565C0',

        gridcolor='rgba(0,0,0,0.10)'
    ),

    # ---------- Overall Font ----------
    font=dict(
        family='Arial',
        color='#1C1C1C'
    ),

    height=600,

    margin=dict(
        l=60,
        r=40,
        t=90,
        b=80
    )
)

# ---------- STREAMLIT ----------
st.plotly_chart(fig4, width='stretch')

# -------------------------------------------------
# WATT WISE ANALYSIS
# -------------------------------------------------

st.markdown('---')
st.markdown('# ⚡ Watt Wise Analysis')

# ---------- Group Data ----------
watt_summary = (

    filtered_df.groupby(
        'Watt',
        as_index=False
    )['Amount']
    .sum()
)

# ---------- Convert to Crores ----------
watt_summary['Revenue_Cr'] = (
    watt_summary['Amount'] / 10000000
)

# ---------- Sort ----------
watt_summary = watt_summary.sort_values(
    by='Revenue_Cr',
    ascending=False
)

# ---------- Treemap ----------
fig5 = px.treemap(

    watt_summary,

    path=['Watt'],

    values='Revenue_Cr',

    color='Revenue_Cr',

    color_continuous_scale=[
        '#DDF5E3',
        '#7BC67E',
        '#008037'
    ],

    title='⚡ Watt Wise Revenue Distribution'
)

# ---------- Treemap Styling ----------
fig5.update_traces(

    textinfo='label+value+percent entry',

    texttemplate=
    '<b>%{label}</b><br>' +
    '₹ %{value:.2f} Cr',

    textfont=dict(
        size=14,
        color='black',
        family='Arial Black'
    ),

    marker=dict(
        line=dict(
            width=2,
            color='white'
        )
    ),

    hovertemplate=
    '<b>Watt:</b> %{label}<br>' +
    '<b>Revenue:</b> ₹ %{value:.2f} Cr<br>' +
    '<b>Contribution:</b> %{percentEntry}<br>' +
    '<extra></extra>'
)

# ---------- Layout ----------
fig5.update_layout(

    # Background
    paper_bgcolor='#FFF8E7',
    plot_bgcolor='#FFF8E7',

    # ---------- Title ----------
    title=dict(

        x=0.5,

        font=dict(
            size=24,
            color='#007A33',
            family='Arial Black'
        )
    ),

    # ---------- Overall Font ----------
    font=dict(
        family='Arial',
        color='#1C1C1C'
    ),

    # ---------- Color Bar ----------
    coloraxis_colorbar=dict(

        title='Revenue',

        titlefont=dict(
            color='black',
            size=14
        ),

        tickfont=dict(
            color='black',
            size=12
        )
    ),

    height=650,

    margin=dict(
        l=20,
        r=20,
        t=80,
        b=20
    )
)

# ---------- Streamlit ----------
st.plotly_chart(fig5, width='stretch')

# -------------------------------------------------
# DATA TABLE
# -------------------------------------------------

st.markdown('---')
st.markdown('# 📋 Data Preview')

st.dataframe(filtered_df.head(10))

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown('---')
st.markdown('### Dashboard Created Using Streamlit + Plotly 🚀')
