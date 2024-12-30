import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Load the data
uploaded_file = "netflix_content_2023.csv"
netflix_data = pd.read_csv(uploaded_file)

# Preprocess data
netflix_data['Hours Viewed'] = netflix_data['Hours Viewed'].replace(',', '', regex=True).astype(float)
netflix_data['Release Date'] = pd.to_datetime(netflix_data['Release Date'], errors='coerce')
netflix_data['Release Month'] = netflix_data['Release Date'].dt.month
netflix_data['Release Day'] = netflix_data['Release Date'].dt.day_name()

# Streamlit app setup
st.set_page_config(page_title="Netflix Dashboard 2023", layout="wide")
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #d81f26;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📺 Netflix Dashboard 2023")
st.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=200)

# Sidebar filters
st.sidebar.header("Filters 🛠️")
content_type = st.sidebar.selectbox("🎬 Select Content Type", netflix_data['Content Type'].dropna().unique())
month_range = st.sidebar.slider("📅 Select Release Month Range", 1, 12, (1, 12))
languages = st.sidebar.multiselect("🌍 Select Languages", netflix_data['Language Indicator'].dropna().unique(), default=None)

# Apply filters
filtered_data = netflix_data[
    (netflix_data['Content Type'] == content_type) & 
    (netflix_data['Release Month'].between(month_range[0], month_range[1]))
]
if languages:
    filtered_data = filtered_data[filtered_data['Language Indicator'].isin(languages)]

# Summary Metrics
st.header("🎯 Summary Metrics")
total_hours = filtered_data['Hours Viewed'].sum()
unique_titles = filtered_data['Title'].nunique()
most_viewed_type = filtered_data.groupby('Content Type')['Hours Viewed'].sum().idxmax()

st.markdown(
    f"""
    - **Total Hours Viewed**: {total_hours:.2f} billion
    - **Number of Unique Titles**: {unique_titles}
    - **Most Viewed Content Type**: {most_viewed_type}
    """
)

# Tabs for insights
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Monthly Viewership", "🌍 Language Trends", "📆 Weekly Patterns",
    "📈 Trends by Type", "🏆 Top Content by Viewership", "📊 Content Distribution"
])

# Viewership by Month
with tab1:
    st.subheader(f"Viewership Hours for {content_type} by Month")
    monthly_viewership = filtered_data.groupby('Release Month')['Hours Viewed'].sum()
    fig1 = px.bar(
        monthly_viewership,
        x=monthly_viewership.index,
        y=monthly_viewership.values,
        labels={'x': 'Month', 'y': 'Hours (in billions)'},
        title=f"Monthly Viewership for {content_type}",
        color_discrete_sequence=["#d81f26"]
    )
    fig1.update_layout(template="plotly_white")
    st.plotly_chart(fig1)

# Language-wise viewership
with tab2:
    st.subheader(f"Language-wise Viewership for {content_type}")
    language_viewership = filtered_data.groupby('Language Indicator')['Hours Viewed'].sum()
    fig2 = px.bar(
        language_viewership,
        x=language_viewership.index,
        y=language_viewership.values,
        labels={'x': 'Language', 'y': 'Hours (in billions)'},
        title=f"Language-wise Viewership for {content_type}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig2.update_layout(template="plotly_white")
    st.plotly_chart(fig2)

# Weekly Release Patterns
with tab3:
    st.subheader("Weekly Release Patterns and Viewership Hours")
    weekday_releases = netflix_data['Release Day'].value_counts().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    weekday_viewership = netflix_data.groupby('Release Day')['Hours Viewed'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )

    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=weekday_releases.index,
            y=weekday_releases.values,
            name='Number of Releases',
            marker_color='blue',
            opacity=0.6,
            yaxis='y1'
        )
    )
    fig3.add_trace(
        go.Scatter(
            x=weekday_viewership.index,
            y=weekday_viewership.values,
            name='Viewership Hours',
            mode='lines+markers',
            marker=dict(color='red'),
            line=dict(color='red'),
            yaxis='y2'
        )
    )
    fig3.update_layout(
        title='Weekly Release Patterns and Viewership Hours (2023)',
        xaxis=dict(title='Day of the Week'),
        yaxis=dict(title='Number of Releases', showgrid=False),
        yaxis2=dict(title='Total Hours Viewed (in billions)', overlaying='y', side='right', showgrid=False),
        height=600,
        width=1000,
        template="plotly_white",
        legend_title="Metrics"
    )
    st.plotly_chart(fig3)

# Viewership Trends by Content Type
with tab4:
    st.subheader("Viewership Trends by Content Type and Release Month")
    monthly_viewership_by_type = netflix_data.pivot_table(index='Release Month', columns='Content Type', values='Hours Viewed', aggfunc='sum')
    fig4 = go.Figure()
    for c_type in monthly_viewership_by_type.columns:
        fig4.add_trace(
            go.Scatter(
                x=monthly_viewership_by_type.index,
                y=monthly_viewership_by_type[c_type],
                mode='lines+markers',
                name=c_type
            )
        )
    fig4.update_layout(
        title='Viewership Trends by Content Type and Release Month (2023)',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        yaxis_title='Total Hours Viewed (in billions)',
        height=600,
        width=1000,
        template="plotly_white",
        legend_title="Content Type"
    )
    st.plotly_chart(fig4)

# Top Content by Viewership
with tab5:
    st.subheader("🏆 Top Content by Viewership")
    top_content = filtered_data[['Title', 'Hours Viewed']].sort_values(by='Hours Viewed', ascending=False).head(10)
    st.table(top_content)

# Content Distribution
with tab6:
    st.subheader("📊 Content Distribution by Type")
    content_distribution = netflix_data['Content Type'].value_counts()
    fig6 = px.pie(
        values=content_distribution.values,
        names=content_distribution.index,
        title="Content Distribution by Type",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig6)

st.info("This dashboard provides a comprehensive view of Netflix content performance in 2023. Copyrights @ Sahaya Gladwin JS")
