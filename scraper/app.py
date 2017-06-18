import json

from scraper import Scraper
from slacklogs import SlackLogs
from s3upload import S3up
import tempfile
import config as cfg


scraper = Scraper()


def log_to_slack(message: str):
    log = SlackLogs()
    print(message)
    log.send(message, "scrapebot", ":penguin:", "scrapelogs")

slackLine = "Tweet Harvester Searching"
# log_to_slack(slackLine)


def load_json_memory(fileName):
    with open(fileName) as data_file:
        return json.load(data_file)


def scrape_cities(filename):

    cities = load_json_memory(filename)

    for city in cities:
        city_geocode = str(city['LATITUDE']) + "," + str(city['LONGITUDE']) + "," + str(city['RADIUS']) + "km"
        tweets = scraper.scrape_city(city['NAME'], city_geocode)

        f = tempfile.SpooledTemporaryFile()
        for item in tweets:
            line = ("%s\n" % item)
            f.write(str.encode(line))
        s3 = S3up(cfg.aws['bucket'])
        s3.upload(f, city['NAME'])


scrape_cities("Melbourne.json")






