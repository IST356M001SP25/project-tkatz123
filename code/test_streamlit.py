import pandas as pd
import streamlit as st

st.title('Test DF')

df = pd.read_csv('cache/cleaned_headlines_us.csv')
st.dataframe(df)

query = (
    "Sentence one. "
    "Sentence two. "
    "Sentence three."
)

st.write(query)