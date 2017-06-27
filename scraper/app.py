import json
import config as cfg
from scraper import Scraper
from slacklogs import SlackLogs
from database import CouchDB
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('tweepy.binder').setLevel(logging.ERROR)
sleep_seconds = 600


def log_to_slack(message: str):
    log = SlackLogs()
    if cfg.prod:
        log.send(message, "scrapebot", ":penguin:", "scrapelogs")
    logger.info(message)


def load_json_memory(file_name):
    with open(file_name) as data_file:
        return json.load(data_file)


def scrape_cities(filename, cityMaxIds=None):
    scraper = Scraper()
    cities = load_json_memory(filename)

    cityMax = {}
    if cityMaxIds is None:
        # Query the database for max tweet id's for each city in the database,
        # set the max id for the city to this if it is unset or greater than the current set value,
        # otherwise use the max_id from the last execution of loop note if you try to always use database the view will
        # sometimes not have indexed and updated meaning tweets are re-downloaded
        # if this is failing its normally because the couchapp 'couchstats' in the project parent hasn't been pushed
        # to the database or the program just hasn't run yet ever on the database
        try:
            for item in CouchDB().get_db().view(name='_design/couchstats/_view/tweetstats', wrapper=None, reduce=True, group_level=2):
                slack_line = "Before scrape run {0} had {1} tweets stored".format(item.key[1], item.value['count'])
                log_to_slack(slack_line)
                if item.key[1] not in cityMax:
                    cityMax[item.key[1]] = item.value['max']
                elif item.value['max'] > cityMax[item.key[1]]:
                    cityMax[item.key[1]] = item.value['max']

        except Exception as e:
            slack_line = "Couldn't get max/min tweet ids for cities Error: {0}".format(str(e))
            log_to_slack(slack_line)
            pass
    else:
        cityMax = cityMaxIds

    for city in cities:
        city_name_ = city['NAME']
        if city_name_ in cityMax:
            this_city_max = cityMax[city_name_]
        else:
            this_city_max = -1
        logger.info('Starting fetch for City: {0}, since_id: {1}'.format(city_name_, this_city_max))
        city_geocode = str(city['LATITUDE']) + "," + str(city['LONGITUDE']) + "," + str(city['RADIUS']) + "km"
        tweets_count, max_id = scraper.scrape_city(city_name=city_name_, city_geocode=city_geocode, since_id=this_city_max)
        cityMax[city_name_] = max_id

    return cityMax


def run():
    log_to_slack("Tweet Harvester Searching")
    if cfg.prod:
        city_file = 'AustraliaCities.json'
    else:
        city_file = "MelbourneSydneyCity.json"
    max_tweet_ids = scrape_cities(city_file)
    while True:
        max_tweet_ids = scrape_cities(city_file, max_tweet_ids)
        logger.info("Sleeping for {0} seconds before starting new run of scraping".format(sleep_seconds))
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    run()

