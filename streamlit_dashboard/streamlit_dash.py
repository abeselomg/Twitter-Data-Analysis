import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from wordcloud import WordCloud
import plotly.express as px
from db import db_execute_fetch


st.set_page_config(page_title="Twitter Data Analysis", layout="wide")

def loadData():
    query = "select * from TweetInformation"
    df = db_execute_fetch(query, dbName="twitter", rdf=True)
    return df

def selectHashTag():
    df = loadData()
    hashTags = st.multiselect("choose combaniation of hashtags", list(df['hashtags'].unique()))
    if hashTags:
        df = df[np.isin(df, hashTags).any(axis=1)]
        st.write(df)

def selectLocAndAuth():
    df = loadData()
    location = st.multiselect("choose Location of tweets", list(df['place'].unique()))
    lang = st.multiselect("choose Language of tweets", list(df['lang'].unique()))

    if location and not lang:
        df = df[np.isin(df, location).any(axis=1)]
        st.write(df)
    elif lang and not location:
        df = df[np.isin(df, lang).any(axis=1)]
        st.write(df)
    elif lang and location:
        location.extend(lang)
        df = df[np.isin(df, location).any(axis=1)]
        st.write(df)
    else:
        st.write(df)

def barChart(data, title, X, Y):
    title = title.title()
    st.title(f'{title} Chart')
    msgChart = (alt.Chart(data).mark_bar().encode(alt.X(f"{X}:N", sort=alt.EncodingSortField(field=f"{Y}", op="values",
                order='ascending')), y=f"{Y}:Q"))
    st.altair_chart(msgChart, use_container_width=True)

def wordCloud():
    df = loadData()
    cleanText = ''
    for text in df['clean_text']:
        tokens = str(text).lower().split()

        cleanText += " ".join(tokens) + " "

    wc = WordCloud(width=650, height=450, background_color='white', min_font_size=5).generate(cleanText)
    st.title("Tweet Text Word Cloud")
    st.image(wc.to_array())

def stBarChart():
    df = loadData()
    dfCount = pd.DataFrame({'Tweet_count': df.groupby(['original_author'])['clean_text'].count()}).reset_index()
    dfCount["original_author"] = dfCount["original_author"].astype(str)
    dfCount = dfCount.sort_values("Tweet_count", ascending=False)

    num = st.slider("Select number of Rankings", 0, 50, 5)
    title = f"Top {num} Ranking By Number of tweets"
    barChart(dfCount.head(num), title, "original_author", "Tweet_count")

def text_category (p):
    if p > 0:
        return 'positive'
    if p < 0:
        return 'negative'
    else:
        return 'neutral'

def langPie():
    df = loadData()
    dfClean = df[['clean_text','polarity', 'subjectivity']]
    
    score = pd.Series([text_category(row_value) for row_value in df['polarity']])
    
    Clean_Tweet = pd.concat([dfClean, score.rename("score")], axis=1)

    dfLangCount = pd.DataFrame({'Tweet_count': Clean_Tweet.groupby(['score'])['clean_text'].count()}).reset_index()
    dfLangCount["score"] = dfLangCount["score"].astype(str)
    dfLangCount = dfLangCount.sort_values("Tweet_count", ascending=False)
    dfLangCount.loc[dfLangCount['score'] == 'positive', 'score'] = 'positive'
    dfLangCount.loc[dfLangCount['score'] == 'negative', 'score'] = 'negative'
    dfLangCount.loc[dfLangCount['score'] == 'neutral', 'score'] = 'neutral'

    st.title(" Positive Tweets Pie Chart")
    fig = px.pie(dfLangCount, values='Tweet_count', names='score', width=500, height=350)
    fig.update_traces(textposition='inside', textinfo='percent+label')

    colB1, colB2 = st.columns([2.5, 1])

    with colB1:
        st.plotly_chart(fig)
    with colB2:
        st.write(dfLangCount)


st.title("Data Display With Filter")
selectHashTag()
st.header("Filter with location")

selectLocAndAuth()
st.title("Charts and Tables")
wordCloud()
with st.expander("Show More Graphs"):
    stBarChart()
    langPie()