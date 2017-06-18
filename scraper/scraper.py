from typing import List, Any
import config as cfg
import tweepy

from slacklogs import SlackLogs


class Scraper(object):
    def __init__(self):
        # todo choose max tweets based on prod / dev
        self.maxTweets = 90
        # self.maxTweets = 1000
        # self.maxTweets = 100000000  # Some arbitrary large number
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

    def scrape_city(self, city_name: str, city_geocode: str, since_id: int=-1, max_id: int=-1) \
            -> List[tweepy.models.Status]:
        tweet_count = 0
        city_tweets = []

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
                    print("No more tweets found")
                    break
                # city_tweets += list(map(lambda x: json.dumps(x._json), new_tweets))
                city_tweets += new_tweets
                tweet_count += len(new_tweets)
                print("Downloaded {0} tweets in {1}".format(tweet_count, city_name))
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                slack_line = "Error while downloading tweets,\n Error: " + str(e)
                self.send_log_slack(slack_line)
                print("some error : " + str(e))

        return city_tweets
