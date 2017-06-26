import json
import config as cfg
from scraper import Scraper
from slacklogs import SlackLogs
from database import CouchDB
import time


def log_to_slack(message: str):
    log = SlackLogs()
    if cfg.prod:
        log.send(message, "scrapebot", ":penguin:", "scrapelogs")
    print(message)


def load_json_memory(file_name):
    with open(file_name) as data_file:
        return json.load(data_file)


def scrape_cities(filename):
    scraper = Scraper()
    cities = load_json_memory(filename)

    cityMax = {}
    # Query the database for max tweet id's for each city in the database,
    # set the max id for the city to this if it is unset or greater than the current set value,
    #  otherwise use the max_id from the last execution of loop note if you try to always use database the view will
    # sometimes not have indexed and updated meaning tweets are re-downloaded
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

    for city in cities:
        if city['NAME'] in cityMax:
            this_city_max = cityMax[city['NAME']]
        else:
            this_city_max = -1
        print('Starting fetch for City: {0}, since_id: {1}'.format(city['NAME'], this_city_max))
        city_geocode = str(city['LATITUDE']) + "," + str(city['LONGITUDE']) + "," + str(city['RADIUS']) + "km"
        tweets_count, max_id = scraper.scrape_city(city_name=city['NAME'], city_geocode=city_geocode, since_id=this_city_max)
        cityMax[city['NAME']] = max_id
        log_string = "{0}: Saved {1} tweets".format(city['NAME'], tweets_count)
        log_to_slack(log_string)


def run():
    while True:
        slackLine = "Tweet Harvester Searching"
        log_to_slack(slackLine)
        if cfg.prod:
            city_file = 'AustraliaCities.json'
        else:
            city_file = "MelbourneCity.json"
        scrape_cities(city_file)
        time.sleep(300)

if __name__ == "__main__":
    run()

