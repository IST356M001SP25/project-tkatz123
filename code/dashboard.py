import streamlit as st
import pandas as pd 
import os
import shutil
import plotly.express as px
import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import ast
from extract import fetch_top_headlines, save_articles_to_csv
from transform import transform_articles

#Defines the webpage title
st.set_page_config(page_title="News Headlines Dashboard", layout="wide")

if 'api_limit_exceeded' not in st.session_state:
    st.session_state.api_limit_exceeded = False

#Specifies the background color and centers the title
st.markdown(
    """
    <style>
    .stApp {
        background-color: #d0ebff; /* Light blue background */
    }
    </style>

    <h1 style='text-align: center;'>News Headlines Dashboard 📰</h1>
    """,
    unsafe_allow_html=True
)

#Function that returns the countries that have cleaned cache files
def get_cached_countries():
    '''
    Returns a list of countries data that is stored in the cache
    '''
    cached_files = os.listdir('cache')
    cached_countries = [
        filename.replace('cleaned_headlines_', '').replace('.csv', '')
        for filename in cached_files
        if filename.startswith('cleaned_headlines_')
    ]

    return cached_countries

def safe_parse_entities(x):
    if isinstance(x, str) and x.strip() not in ["", "[]"]:
        try:
            return ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return []
    elif isinstance(x, list):
        return x
    else:
        return []

if 'country_code' not in st.session_state:
    st.session_state.country_code = 'Select a Country...'

#All the countries the news API supports
all_country_codes = ['us', 'gb', 'ca', 'au']

#Sets the API daily limit to false
api_limit_exceeded = False

#If the API daily limit is exceeded only uses countries with data already in the cache
if api_limit_exceeded:
    dropdown_options = get_cached_countries()
else:
    dropdown_options = all_country_codes

#Creates a sidebar dropdown menu to select country
dropdown_options = ['Select a Country...'] + sorted(dropdown_options)
st.sidebar.header("🔎 Filter Options")
country_code = st.sidebar.selectbox(
    "Select a Country",
    options=dropdown_options,
    index=dropdown_options.index(st.session_state.country_code),
    key='country_code'
)

st.sidebar.markdown("### Admin Controls ⚙️")

# Add a clear cache button
if st.sidebar.button("Clear Cache 🗑️"):
    cache_dir = 'cache'
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                st.error(f"Failed to delete {filename}: {e}")
        if 'country_code' in st.session_state:
            del st.session_state['country_code']
        st.session_state.cache_cleared = True
        st.rerun()
    else:
        st.info("📂 Cache folder does not exist.")

if st.session_state.get("cache_cleared", False):
    st.success("✅ Cache cleared successfully!")
    del st.session_state["cache_cleared"]

#When a country is selected run the following
if country_code != 'Select a Country...':
    
    if st.session_state.get('api_limit_exceeded', False):
        st.error("❌ API limit was already exceeded. Please use cached data.")
        st.stop()

    #Gets the filepath name for the clean data (end result of pipeline)
    cleaned_file_path = f'cache/cleaned_headlines_{country_code.lower()}.csv'

    #If the selected countries clean data already exists...
    if os.path.exists(cleaned_file_path):
        st.success(f"✅ Loaded cached cleaned headlines for '{country_code.upper()}'") #Display loaded cache data
        df = pd.read_csv(cleaned_file_path) #Sets the cleaned data to DF
        if 'entities' in df.columns:
            df['entities'] = df['entities'].apply(safe_parse_entities)
        else:
            df['entities'] = [[] for _ in range(len(df))]
    else: #If the selected countries clean data doesn't exist in cache

        try:
            st.info(f"🔄 Fetching fresh top headlines for '{country_code.upper()}'...")

            #Extract raw headlines
            articles = fetch_top_headlines(country_code.lower())
            st.write(f"🔎 Articles fetched: {len(articles)}")

            if len(articles) == 0:
                st.error(f"❌ No news articles found for '{country_code.upper()}' at this time. Please select another country.")
                st.stop()

            #Save raw headlines to CSV
            save_articles_to_csv(articles, country_code.lower())
            st.write(f"✅ Saved raw articles to cache/top_headlines_{country_code.lower()}.csv")

            st.info(f"⏰This step may take a minute. Please be patient")

            #Transform raw headlines into cleaned DF
            transform_articles(country_code.lower())
            df = pd.read_csv(cleaned_file_path)
            if 'entities' in df.columns:
                df['entities'] = df['entities'].apply(safe_parse_entities)
            else:
                df['entities'] = [[] for _ in range(len(df))]

            #Displays success message when loaded
            st.success(f"✅ Successfully cleaned and cached headlines for '{country_code.upper()}'")

        except Exception as e:
            #If API error because of daily usage limit, switch to cached-only mode
            if "Daily API usage" in str(e):
                st.session_state.api_limit_exceeded = True
                st.error("❌ API daily usage limit exceeded. Please use a cached country or try again later.")
                st.stop()
            else:
                st.error(f"❌ Error loading data: {e}")
                st.stop()

    st.subheader(f"Preview of 3 Top Headlines in {country_code.upper()} 🎥")

    # Function to get 3 random rows
    def get_random_articles(df):
        return df.sample(n=3)

    # Initialize session state for random articles
    if 'random_articles' not in st.session_state:
        st.session_state.random_articles = get_random_articles(df)

    # Display the table
    preview_df = st.session_state.random_articles[['short_title', 'topic', 'sentiment']].reset_index(drop=True)
    st.table(preview_df)

    # Button to reshuffle and get new random articles
    if st.button('🔄 Refresh Top Headlines'):
        st.session_state.random_articles = get_random_articles(df)
        st.rerun()

    st.subheader("Authors and Their Articles (Short Titles) ✍️")

    # Drop rows with missing authors
    authors = df.dropna(subset=['author'])

    # Group titles under each author
    grouped = authors.groupby('author')['short_title'].apply(list).reset_index()

    # Display authors with expanders
    for _, row in grouped.iterrows():
        with st.expander(row['author']):
            for title in row['short_title']:
                st.markdown(f"- {title}")
    
    st.subheader(f'{country_code.upper()} Top Headlines Analysis📈')

    ##TOPIC BAR CHART / SENTIMENT BAR CHART

    #Gets the count of the topics in the data 
    topic_counts = df['topic'].value_counts().reset_index()
    topic_counts.columns = ['Topic', 'Article Count']

    #Gets count of the sentiment in the data 
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']

    #Create Streamlit columns
    col1, col2 = st.columns(2)

    with col1:
        #Plots the top 10 topics using Plotly 
        fig = px.bar(
            topic_counts.head(10),
            x = 'Topic',
            y = 'Article Count',
            color = 'Topic',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        #Updates titles, axis labels, and background color of plot
        fig.update_layout(
        title=f'Top Topics by Article Count in The {country_code.upper()}',
        xaxis_title='Topic',
        yaxis_title='Number of Articles',
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0'
        )

        #Sets text position and axis titles
        fig.update_traces(textposition = 'outside')
        fig.update_layout(xaxis_title = 'Topic', yaxis_title = 'Number of Articles')

        #Displays the plot
        st.plotly_chart(fig, use_container_width= True)

    with col2:
        
        colors = px.colors.qualitative.Set3

        sentiment_color_map = {
                'positive': colors[0],
                'neutral': colors[1],
                'negative': colors[2]
            }

        #Creates pie chart of the distribution of sentiment among the articles
        fig_pie = px.pie(
        sentiment_counts,
        names='Sentiment',
        values='Count',
        color='Sentiment',
        color_discrete_map= sentiment_color_map,
        title='Sentiment Distribution of Articles'
        )

        #Sets the background color of the plot
        fig_pie.update_layout(
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0'
        )

        #Sets text position and plots piechart
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    ##PUBLISHED TIME OF DAY BAR CHART
    st.subheader("Article Publication Trends📊")

    #Chooses the level of aggregation for chart
    group_by_option = st.selectbox(
    "Group Articles By:",
    ("Time of Day", "Day of Week", "Month Published")
    )

    #If time of day selected, order the time of day chronologically and count the values
    if group_by_option == "Time of Day":
        group_col = 'time_of_day_published'
        time_order = [
            "12AM-3AM", "3AM-6AM", "6AM-9AM", "9AM-12PM",
            "12PM-3PM", "3PM-6PM", "6PM-9PM", "9PM-12AM"
        ]
        counts = df[group_col].value_counts().reindex(time_order).reset_index()
        counts.columns = [group_col, 'Article Count']

    #If day of week chosen, order the day of week chronologically and count the values
    elif group_by_option == "Day of Week":
        group_col = 'day_of_week_published'
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        counts = df[group_col].value_counts().reindex(day_order).reset_index()
        counts.columns = [group_col, 'Article Count']

    #If niether of the other two are chosen, aggregate by month and sort in chronolical order
    else:  # Month Published
        group_col = 'month_published'
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        counts = df[group_col].value_counts().reindex(month_order).dropna().reset_index()
        counts.columns = [group_col, 'Article Count']

    #Creates the bar chart with same color scheme as other graphs
    fig_trends = px.bar(
    counts,
    x=group_col,
    y='Article Count',
    color=group_col,
    color_discrete_sequence=px.colors.qualitative.Set3,
    title=f"Articles Published by {group_by_option}"
    )

    #Sets background color and axis labels
    fig_trends.update_layout(
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        xaxis_title=group_by_option,
        yaxis_title="Number of Articles"
    )

    #Displays the chart
    st.plotly_chart(fig_trends, use_container_width=True)

    ##WORD CLOUD
    st.subheader("☁️ Entity Word Cloud by Topic")

    # Dropdown to select a topic from articles
    unique_topics = sorted(df['topic'].dropna().unique())
    selected_topic = st.selectbox("Choose a Topic", unique_topics)

    # Filter to rows that match selected topic
    filtered_df = df[df['topic'] == selected_topic]

    #Combines the list of entities into a single list
    all_entities = []
    for entities in filtered_df['entities']:
        if isinstance(entities, list):
            all_entities.extend(entities)

    # Generate the word cloud only if there are entities, using same colors as other plots
    if all_entities:
        entity_text = " ".join(all_entities)
        wordcloud = WordCloud(width=700, height=300, background_color='#f0f0f0', colormap='Set3').generate(entity_text)

        # Display word cloud
        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)
    else:
        st.info("No entities available for this topic.")
