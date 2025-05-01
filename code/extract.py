import requests
import pandas as pd
import os

NEWSAPI_KEY = 'SEE EMAIL FOR API KEY'

def fetch_top_headlines(country_code, page_size = 100, language = 'en'):
    '''
    Retrieves the top headline articles for inputed country. 
    Enter the country code for desired country. EX: us
    Page_size restricted to 100 because the free API access only allows pulling 100 articles at a time.
    Specifies to pull articles only in eEglish
    '''
    url = "https://newsapi.org/v2/top-headlines"
    headers = {'X-API-Key': NEWSAPI_KEY}
    params = {
        'country': country_code.lower(), #Converts country code to lower for API requirement
        'pageSize': page_size, #Restrictred to 100 due to API limits
        'language': language #Specifies to pull files only in English
    }

    #Makes request to API based on parameters
    response = requests.get(url, headers = headers, params = params)

    #If the status code was 200 return the json, if not display the status code and the reason for error
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        return articles
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return []
    
def save_articles_to_csv(articles, country_code):
    '''
    Saves 10 articles from API request to cache, avoiding unnecesary API requests
    '''
    #Runs code if articles exist
    if articles:

        limited_articles = articles[:15]

        #Converts articles to DF
        df = pd.json_normalize(
            limited_articles,
            record_path= None,
            meta = ['source.id', 'source.name', 'author', 'title', 'description', 'url', 'urlToImage',
                    'publishedAt', 'content'],
            sep = '_'
        )

        #Specifies the filename for creating CSV
        filename = f'top_headlines_{country_code.lower()}.csv'

        #Joining the cache directory with the filename
        cache_path = os.path.join('cache', filename)

        #Exporting df to CSV and ignoring the index's
        df.to_csv(cache_path, index = False)

        #Print how many articles where succesfully saved
        print(f'Saved {len(df)} articles to {cache_path}')
    else:

        #If no articles exist to be saved, state it
        print('No articles to save.')


if __name__ == "__main__":
    
    country_code = 'us'
    articles = fetch_top_headlines(country_code)
    save_articles_to_csv(articles, country_code)
