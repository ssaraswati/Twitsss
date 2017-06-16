from slacklogs import SlackLogs
from scraper import Scraper
import json
import config as cfg

scraper = Scraper()

def sendtoLogsChannel(message):
    log = SlackLogs()
    print(message)
    log.send(message, "scrapebot", ":penguin:", "scrapelogs")

slackLine = "Tweet Harvester Searching"
# sendtoLogsChannel(slackLine)

def load_json_memory(fileName):
    with open(fileName) as data_file:
        return json.load(data_file)

def melbournetofile():
    with open('melbourneDev', 'w') as f:
        tweets = scraper.scrape_city("Melbourne", "-37.9,144.5,100km")
        for item in tweets:
            f.write("%s\n" % item)

def australiatofile():

    australiaCities = load_json_memory("AustraliaCities.json")

    for city in australiaCities:

        with open(city['NAME'], 'a') as f:
            cityGeocode = str(city['LATITUDE']) + "," + str(city['LONGITUDE']) + "," + str(city['RADIUS']) + "km"
            tweets = scraper.scrape_city(city['NAME'], cityGeocode)

            for item in tweets:
                f.write("%s\n" % item)


australiatofile()






