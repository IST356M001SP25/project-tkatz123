# About My Project

Student Name: Tyler Katz
Student Email:  tmkatz@syr.edu

### What it does

This projeett uses the News API to pull the top headline articles off the internet for a designated country. The articles are updated every 24 hours and can range from 0 to 100 articles per country. The information on the articles include the author, title, description, url, urlToImage, publishedAt, content, source_id, and source_name. After obtaining this data I feature engineered several columns including short_title, day_of_week_published, month_published, and time_of_day_published. Additionally, I used API's provided by the iSchool to get the sentiment, entities, and topic of each article. I culminated all of these features in a streamlit dashboard which allows the user to explore differen't aspects of the data.

### How you run my project
- Firstly, make sure you are running Python version 3.11.0

-Next make sure you download all the required packages by running this command in the terminal:

    pip install -r requirements.txt

-Then open the extract.py file in the code folder and insert your API key for the News API at the top of the file. You can obtain an API key by creating a free account on this website: https://newsapi.org/

-After that, open up the transform.py file in the code folder and insert your iSchool API key at the top of the file. You can obtain this API key by logging in with your SUID on this website: https://cent.ischool-iot.net/

-After that you should be all good to go to run the streamlit dashboard!

-NOTE: You may have to create a 'cache' folder if one doesn't download with the project

### Other things you need to know

When I started this project I was under the impression I would be able to access all 50 countries the API offers. But when I got to the dashboard step I realized that the free access to the API only allowed acces to the US, England, Canada, and Australia. However, England, Canada, and Australia don't always have top headlines available but the U.S. always does. By the time I realized it, I had spent too much time on the project to restart and considered upgrading to the next level of the API to solve this issue but it's $500 dollars a month. Please take this into consideration when grading as it's a restriction by the API, my code is still designed to be able to make requests to any of the available countries if I could. I worked around this issue by limiting the inputs of the streamlit to the four countries above, and if one of the countries doesn't have headlines that day, the streamlit notifies the user without causing an error. I also had to limit the code to only 10 articles per API request because if there was more data the full code would make around 100 calls to the iSchool API's and the code wouldn't work most of the time. You will need around 45 API calls available to run this project. I've pushed cleaned article CSV files for the US, so if you don't have API calls avaible when grading, choose US on the streamlit and the dashboard will run without having to make any API calls. If you do have them available, use the clear cache button then choose US.