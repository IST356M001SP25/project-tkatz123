import os
import pandas as pd 
from code.extract import fetch_top_headlines, save_articles_to_csv

def test_should_pass():
    print("\n Always True!")
    assert True

def test_fetch_top_headlines():

    #Calls fetch_top_headlines with country code: us
    country_code = 'us'
    articles = fetch_top_headlines(country_code)

    #Checks that the result of the function call is a list of articles
    assert isinstance(articles, list)

    #Tests that each article in the list is a dictionary
    if articles:
        assert isinstance(articles[0], dict)

def test_save_articles_to_csv():

    #Creating a fake sample article to test 
    articles = [
        {
            "source": {"id": None, "name": "Test Source"},
            "author": "Test Author",
            "title": "Test Title",
            "description": "Test Description",
            "url": "https://testurl.com",
            "urlToImage": "https://testurl.com/image.png",
            "publishedAt": "2025-04-28T12:00:00Z",
            "content": "Test content."
        }
    ]

    #Calling function using test article
    save_articles_to_csv(articles, 'test')

    #Creates the filepath to check if the article exists
    filepath = os.path.join('cache', 'top_headlines_test.csv')
    assert os.path.exists(filepath)

    #Reads in the test article CSV as a dataframe
    df = pd.read_csv(filepath)

    #Tests if dataframe is empty
    assert not df.empty

    #Test if title column exists in dataframe
    assert 'title' in df.columns

    #Removes the test article from the cache
    os.remove(filepath)