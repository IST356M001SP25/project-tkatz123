import pandas as pd
import requests
import os
import re
from datetime import datetime

APIKEY = 'ADD YOUR API KEY'

##HELPER FUNCTIONS

def clean_text(text):
    '''
    Cleans a text string:
        -Replaces multiple white spaces with a single white space
        -Removes newlines 
        -Strips extra space
    '''

    #Ensures text isn't empty to avoid errors
    if pd.isnull(text):
        return ""
    
    #Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)

    #Removes newline characters
    text = re.sub(r'\n|\r', '', text)

    #Strips and returns text
    return text.strip()

def create_short_title(title, num_words = 10):
    '''
    Returns the first 'num_words' from a title string
    '''
    
    #Ensures title isn't null to avoid errors
    if pd.isnull(title): 
        return ""
    
    #Splits inputted title into a list of words
    words = title.split()

    #Creates a shortened title seperating each of the first 8 word with a space
    shortened_title = ' '.join(words[:num_words])
    return shortened_title

def get_sentiment(text):
    '''
    Sends text to the sentiment analysis API and returns the sentiment
    '''

    #Ensures text is not empty to avoid errors
    if not text:
        return None
    
    #Specifying API URL, headers and data 
    url = 'https://cent.ischool-iot.net/api/azure/sentiment'
    headers = {'X-API-KEY': APIKEY}
    data = {'text': text}

    #Wraps API call in try accept statement to avoid crashes
    try:
        response = requests.post(url, headers= headers, data = data, timeout= 60) #Makes call to the API
        if response.status_code == 200: #Only returns result if success code is returned
            result = response.json()
            return result['results']['documents'][0]['sentiment']
        else: #If API call is unsuccesful print the reasons
            print(f"Sentiment API error {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Sentiment API exception: {e}") #If there is an exception in the API call returns reason instead of crashing
        return None
    
def get_entities(text):
    '''
    Sends text to the entity recognition API and returns a list of entities
    '''

    #Ensures text is not empty to avoid crashes
    if not text:
        return None
    
    #Specifies URL, headers, and data for call to API
    url = 'https://cent.ischool-iot.net/api/azure/entityrecognition'
    headers = {'X-API-KEY': APIKEY}
    data = {'text': text}

    #Wraps API call in try statement to avoid crashing
    try:
        #Calls to API
        response = requests.post(url, headers = headers, data = data, timeout= 60)
        if response.status_code == 200: #Only runs if success code is returned
            result = response.json()
            documents = result['results']['documents'] #Stores a list of documents
            if documents: #Only runs if documents exist
                entity_list = []
                for entity in documents[0]['entities']: #Iteratres over each document and extracts the entity
                    entity_list.append(entity['text'])
                return entity_list
            else:
                return []
        else: #If API call is unsuccesful print the reasons
            print(f'Entitiy API error {response.status_code} - {response.text}')
            return []
    except Exception as e:
        print(f'Entity API exception: {e}') #If there is an exception in the API call returns reason instead of crashing
        return []
    
def get_topic_from_entities(entities):
    '''
    Sends a list of entities to the GenAI APi to generate 1-2 word topic label
    '''

    #Ensures entities is not empty to avoid crashes
    if not entities:
        return "Unknown"
    
    #Joins all the elements of the entities list together into one string
    entities_text = ', '.join(entities)

    #Defines what the GenAI should do
    query = (
    f"Given these entities: {entities_text}."
    "Respond with only a one or two-word topic that best summarizes them."
    "Do not explain. Do not give reasoning. Only respond with the one or two-word topic name."
    "Make them broad, for example if the entities are things like Nasdaq, stock, 0.1% the topic should be finance,"
    "If the entities are United States, immegrants, federal raid the topic should be politics"
    )

    #Specifying URL, headers, and data 
    url = 'https://cent.ischool-iot.net/api/genai/generate'
    headers = {'X-API-KEY': APIKEY}
    data = {
        'query': query,
        'temperature': 0.3 #Temperature set to 0.3 for less random responses
    }

    #Wraps API call in try except statement to avoid crashes
    try:
        #Calls to API
        response = requests.post(url, headers = headers, data = data, timeout= 60)
        if response.status_code == 200: #Only runs of API status code is succesfukl
            topic = response.json().strip() #Strips response
            return topic if topic else "Unknown" #Return topci if it exists otherwise returns unknown
        else: #If API call is unsuccesful print the reasons
            print(f'GenAI API error {response.status_code} - {response.text}')
            return 'Unknown'
    except Exception as e:
        print(f'GenAI API exception: {e}') #If there is an exception in the API call returns reason instead of crashing
        return "Unknown"
    
def categorize_time_of_day(hour):
    '''
    Categorizes hour of day into 3-hour time block
    '''

    if 0 <= hour < 3:
        return "12AM-3AM"
    elif 3 <= hour < 6:
        return "3AM-6AM"
    elif 6 <= hour < 9:
        return "6AM-9AM"
    elif 9 <= hour < 12:
        return "9AM-12PM"
    elif 12 <= hour < 15:
        return "12PM-3PM"
    elif 15 <= hour < 18:
        return "3PM-6PM"
    elif 18 <= hour < 21:
        return "6PM-9PM"
    else:
        return "9PM-12AM"

def remove_numeric_entities(entity_list):
    '''
    Removes entities that are pure numbers from the list
    '''

    #Removes normal numbers, decimals, and percentages from entity list
    if not entity_list:
        return []
    return [e for e in entity_list if not re.fullmatch(r'[\d,]+(\.\d+)?%?', e)]

##MAIN TRANSFORMATION PIPELINE

def transform_articles(country_code):
    '''
    Combines all helper functions into a final transormation pipeline to add all features to data
    '''

    #Loading raw article data for specified country
    filepath = os.path.join('cache', f'top_headlines_{country_code.lower()}.csv')
    df = pd.read_csv(filepath)

    #Filter out empty articles
    df = df.dropna(subset= ['title', 'content'])

    #Applies clean text to all the text fields
    for field in ['title', 'description', 'content']:
        df[field] = df[field].apply(clean_text)
    
    #Creates short title for each article
    df['short_title'] = df['title'].apply(create_short_title)
    
    #Gets sentiment for each article
    df['sentiment'] = df['content'].apply(get_sentiment)

    #Gets entities of each article
    df['entities'] = df['content'].apply(get_entities)

    #Removes numeric values from entities 
    df['entities'] = df['entities'].apply(remove_numeric_entities)

    #Gets topic of each article based on entities
    df['topic'] = df['entities'].apply(get_topic_from_entities)
    
    #Parse publishedAt converting it to datetime, if there is an error a null value is put in place
    df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors = 'coerce')

    #Gets time of day article was published
    df['day_of_week_published'] = df['publishedAt'].dt.day_name()

    #Gets month article was published
    df['month_published'] = df['publishedAt'].dt.month_name()

    #Categorizes time of publish into group of 3 hour block
    df['time_of_day_published'] = df['publishedAt'].dt.hour.apply(categorize_time_of_day)

    #Writes cleaned data to cache
    savepath = os.path.join('cache', f'cleaned_headlines_{country_code.lower()}.csv')
    df.to_csv(savepath, index = False)
    print(f'Saved cleaned data to {savepath}')

if __name__ == "__main__":
    country_code = 'us'
    transform_articles(country_code)