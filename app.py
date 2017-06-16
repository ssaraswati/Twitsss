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


with open('workfile', 'w') as f:
    tweets = scraper.scrape_city("Melbourne","-37.9,144.5,100km")
    for item in tweets:
        f.write("%s\n" % item)






