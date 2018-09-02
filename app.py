import sys, os, json, datetime, time, logging
import tweepy
import os
from logstyles import BraceMessage as __

class WriteBuffer:
    tweets = []
    def __init__(self, prefix, buffersize):
        self.prefix = prefix
        self.buffersize = buffersize

    def add_tweet(self, tweet):
        """
        adds tweet to the current buffer, clears the buffer if greater tha buffer size
        :param tweet: Json tweet
        """
        self.tweets.append(tweet)
        tweets_in_buffer = len(self.tweets)
        add_msg = 'Buffer size:{0}/{3} Latest tweet: {1} id: {2}'
        logging.info(__(add_msg, tweets_in_buffer, tweet['text'], tweet['id_str'], self.buffersize))
        if tweets_in_buffer >= self.buffersize:
            self.write_tweets()

    def write_tweets(self):
        """
        Write the tweets to storeage and clears the buffer
        """
        path = '{0}/{1}.json'.format(self.prefix, int(time.time()))
        try:         
            with open(path, 'w') as outfile:
                json.dump(self.tweets, outfile)
            logging.info(__('Saved {0} tweets to {1}', self.tweets, path))
            self.tweets = []
        except:
            logging.error(__('Failed to save {0} tweets {1}', self.tweets, path))


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, data_store, geo_only=True):
        """
        registers a data repository to store tweets in
        :param data_store: object that implements add_tweet(json_tweet)
        """
        super().__init__()
        self.datastore = data_store
        self.geo_only = geo_only


    def on_status(self, status):
        tweet_json = status._json
        if self.datastore is None:
            logging.critical('Nothing to do with tweets no datastore...Exiting')
            sys.exit()
        if not self.geo_only:
            self.datastore.add_tweet(tweet_json)
        elif self.geo_only and tweet_json['coordinates'] is not None:
            self.datastore.add_tweet(tweet_json)

    def on_error(self, status_code):
        logging.error(__('Encountered error with status code: {0}', status_code))
        return True # Don't kill the stream

    def on_timeout(self):
        logging.error('Timeout...')
        return True # Don't kill the stream

def run():
    logging.info(__('Starting tweet to s3 streaming scraper @ {0}', datetime.datetime.now()))

    bounding = [float(i) for i in os.environ.get("BOUNDING_BOX").split(",")]
    
    tweetBuffer = WriteBuffer(os.environ['DATA_PATH'], int(os.environ['BUFFER_SIZE']))

    auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'],
                               os.environ['TWITTER_CONSUMER_SECRET'])

    auth.set_access_token(os.environ['TWITTER_ACCESS_KEY'],
                          os.environ['TWITTER_ACCESS_SECRET'])
    tweepy.API(auth)
    connect_msg = 'Connected to twitter with consumer key: {0}, {1} access_secret: *****'
    logging.info(__(connect_msg, os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_ACCESS_KEY']))
    logging.info(__('Using Location filter with bounding box of {0}', bounding))
    listener = CustomStreamListener(tweetBuffer, bool(os.environ['GEO_ONLY']))
    tweet_stream = tweepy.streaming.Stream(auth, listener)
    tweet_stream.filter(locations=bounding)

if __name__ == "__main__":
    print("Starting tweet scraper")
    LOG_STRING = "[%(asctime)s] %(levelname)s %(name)s:%(funcName)s:%(lineno)s - %(message)s"
    logging.basicConfig(format=LOG_STRING, level=logging.ERROR)
    run()
