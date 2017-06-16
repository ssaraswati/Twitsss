import json

import config as cfg
import tweepy

from scraper.slacklogs import SlackLogs


class Scraper(object):

    def __init__(self):
        self.sinceId = None
        self.max_id = -1

        self.maxTweets = 250
        # self.maxTweets = 100000000  # Some arbitrary large number
        self.tweetsPerQry = 100  # this is the max the API permits

        consumer_key = cfg.twitter['consumer_key']
        consumer_secret = cfg.twitter['consumer_secret']

        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)

    def sendtoLogsChannel(self, message):
        log = SlackLogs()
        log.send(message, "scrapebot", ":penguin:", "scrapelogs")


    def scrape_city(self, cityName, cityGeocode):
        tweetCount = 0
        cityTweets = []

        while tweetCount < self.maxTweets:
            try:
                if (self.max_id <= 0):
                    if (not self.sinceId):
                        new_tweets = self.api.search(geocode=cityGeocode, count=self.tweetsPerQry)
                    else:
                        new_tweets = self.api.search(geocode=cityGeocode, count=self.tweetsPerQry,
                                                since_id=self.sinceId)
                else:
                    if (not self.sinceId):
                        new_tweets = self.api.search(geocode=cityGeocode, count=self.tweetsPerQry,
                                                max_id=str(max_id - 1))
                    else:
                        new_tweets = self.api.search(geocode=cityGeocode, count=self.tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=self.sinceId)
                if not new_tweets:
                    print("No more tweets found")
                    break
                cityTweets += list(map(lambda x: json.dumps(x._json), new_tweets))

                tweetCount += len(new_tweets)
                print("Downloaded {0} tweets in {1}".format(tweetCount, cityName))
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                slackLine = "Error while downloading tweets,\n Error: " + str(e)
                self.sendtoLogsChannel(slackLine)
                print("some error : " + str(e))

        return cityTweets
