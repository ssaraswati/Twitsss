import json

from scraper import Scraper
from slacklogs import SlackLogs
from database import CouchDB
scraper = Scraper()


def log_to_slack(message: str):
    log = SlackLogs()
    print(message)
    log.send(message, "scrapebot", ":penguin:", "scrapelogs")

slackLine = "Tweet Harvester Searching"
# todo log if prod
# log_to_slack(slackLine)


def load_json_memory(file_name):
    with open(file_name) as data_file:
        return json.load(data_file)


def scrape_cities(filename):

    cities = load_json_memory(filename)

    for city in cities:
        city_geocode = str(city['LATITUDE']) + "," + str(city['LONGITUDE']) + "," + str(city['RADIUS']) + "km"
        tweets = scraper.scrape_city(city_name=city['NAME'], city_geocode=city_geocode)

        tweets_to_save = []
        for tweet in tweets:
            db_item = {
                '_id': str(tweet.id),
                'id': tweet.id,
                'created_at': tweet.created_at.isoformat(),
                'text': tweet.text,
                'city': city['NAME'],
                'user_id': tweet.user.id,
                'user_home': tweet.user.location,
                'iso_language_code': tweet.metadata['iso_language_code'],
                'coordinates': tweet.coordinates,
                'source': tweet.source,
                'type': 'tweet'
                       }
            tweets_to_save.append(db_item)
        # send the tweets as a batch
        couch = CouchDB()
        couch.update(tweets_to_save)

scrape_cities("MelbourneSydneyCity.json")

