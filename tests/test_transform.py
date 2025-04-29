import pytest
from code.transform import (
    clean_text,
    create_short_title,
    remove_numeric_entities,
    categorize_time_of_day,
    get_sentiment,
    get_entities,
    get_topic_from_entities
)

def test_should_pass():
    print("\n Always True!")
    assert True

#This function removes white space and new line values from text
def test_clean_text():
    assert clean_text("This   is  a\n\n test.") == "This is a test."
    assert clean_text(None) == ""
    assert clean_text("Already clean") == "Already clean"

#This function shortens a title to the first 8 words
def test_create_short_title():
    assert create_short_title("This is a very long title that should be shortened") == "This is a very long title that should"
    assert create_short_title("") == ""
    assert create_short_title(None) == ""

#This function removes different formats of numbers from the entities list
def test_remove_numeric_entities():
    assert remove_numeric_entities(["NASA", "Mars", "2025", "1500", "1,500"]) == ["NASA", "Mars"]
    assert remove_numeric_entities(["NASA", "15.5", "50%", "99.9%"]) == ["NASA"]
    assert remove_numeric_entities(["Elon Musk", "SpaceX", "1000"]) == ["Elon Musk", "SpaceX"]

#This function tests that hours of day are correctly categorized
def test_categorize_time_of_day():
    assert categorize_time_of_day(0) == "12AM-3AM"
    assert categorize_time_of_day(4) == "3AM-6AM"
    assert categorize_time_of_day(7) == "6AM-9AM"
    assert categorize_time_of_day(10) == "9AM-12PM"
    assert categorize_time_of_day(13) == "12PM-3PM"
    assert categorize_time_of_day(16) == "3PM-6PM"
    assert categorize_time_of_day(19) == "6PM-9PM"
    assert categorize_time_of_day(22) == "9PM-12AM"

#This function tests that a sample sentance is of one of the three possible sentiment results
def test_get_sentiment():
    sentiment = get_sentiment("I love learning new things.")
    assert sentiment in ["positive", "neutral", "negative"]

#This function tests that the entities list isn't empty
def test_get_entities():
    entities = get_entities("NASA is planning a new Mars mission.")
    assert isinstance(entities, list)
    assert len(entities) > 0

#This function tests that the topic isn't blank
def test_get_topic_from_entities():
    topic = get_topic_from_entities(["NASA", "Mars", "rover"])
    assert isinstance(topic, str)
    assert len(topic) > 0