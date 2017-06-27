from typing import Union, Tuple

import tweepy

import config as cfg
from database import CouchDB
from slacklogs import SlackLogs
from tweet import Tweet
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Scraper(object):
    def __init__(self):
        self.maxTweets = cfg.get_fetch_size()
        self.tweetsPerQry = 100  # this is the max the API permits

        consumer_key = cfg.twitter['consumer_key']
        consumer_secret = cfg.twitter['consumer_secret']

        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)

    @staticmethod
    def send_log_slack(message: str):
        log = SlackLogs()
        log.send(message, "scrapebot", ":penguin:", "scrapelogs")

    def scrape_city(self, city_name: str, city_geocode: str, since_id: int = -1, max_id: int = -1) \
            -> Tuple[Union[int, int], Union[int, int]]:
        tweet_count = 0

        while tweet_count < self.maxTweets:
            try:
                if max_id <= 0:
                    if since_id <= 0:
                        new_tweets = self.api.search(geocode=city_geocode, count=self.tweetsPerQry)
                    else:
                        new_tweets = self.api.search(geocode=city_geocode, count=self.tweetsPerQry,
                                                     since_id=since_id)
                else:
                    if since_id <= 0:
                        new_tweets = self.api.search(geocode=city_geocode, count=self.tweetsPerQry,
                                                     max_id=str(max_id - 1))
                    else:
                        new_tweets = self.api.search(geocode=city_geocode, count=self.tweetsPerQry,
                                                     max_id=str(max_id - 1),
                                                     since_id=since_id)
                if not new_tweets:
                    logger.info("No more tweets found")
                    break

                tweets_to_save = []
                for tweet in new_tweets:
                    db_item = Tweet(id=str(tweet.id),
                                    created_at=tweet.created_at,
                                    text=tweet.text,
                                    city=city_name,
                                    user_id=tweet.user.id,
                                    user_home=tweet.user.location,
                                    source=tweet.source,
                                    type='tweet')
                    if tweet.coordinates:
                        latitude, longitude = tweet.coordinates['coordinates']
                        db_item.latitude = latitude
                        db_item.longitude = longitude

                    tweets_to_save.append(db_item)

                couch = CouchDB()
                couch.update(tweets_to_save)

                tweet_count += len(tweets_to_save)

                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                slack_line = "Error while downloading tweets,\n Error: " + str(e)
                self.send_log_slack(slack_line)
                logger.error("some error : " + str(e))
        logger.info("Downloaded {0} tweets in {1}".format(tweet_count, city_name))
        return tweet_count, max_id
