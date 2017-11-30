import sys, os, json, datetime, time, logging
import tweepy
import boto3
from boto3.session import Session
import os
from logstyles import BraceMessage as __

class AWSS3UploadBuffer:
    tweets = []
    def __init__(self, aws_access_key_id, aws_secret_access_key, region, bucket_name, prefix, buffersize):
        self.session = Session(aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key,
                               region_name=region)
        self.s3 = self.session.resource("s3")
        self.bucket_name = bucket_name
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
            self.upload_now()

    def upload_now(self):
        """
        Uploads the current buffer of tweets to s3 and clears the buffer
        """
        keyprefix = '' if self.prefix is None else self.prefix + '/'
        key = '{0}{1}.json'.format(keyprefix, int(time.time()))
        json_content_type = {'Content-Type': 'application/json'}
        try:
            s3_object = self.s3.Object(self.bucket_name, key)
            s3_object.put(Body=json.dumps(self.tweets), Metadata=json_content_type)
            logging.info(__('Saved {0} tweets to s3 bucket: {1} key: {2}', self.tweets, self.bucket_name, key))
            self.tweets = []
        except:
            logging.error(__('Failed to save {0} tweets to s3 bucket: {1} key: {2}', self.tweets, self.bucket_name, key))


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
    
    s3buffer = AWSS3UploadBuffer(os.environ['AWS_REGION'],
                                 os.environ['AWS_BUCKET_NAME'],
                                 os.environ['AWS_BUCKET_PREFIX'],
                                 100)

    auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'],
                               os.environ['TWITTER_CONSUMER_SECRET'])

    auth.set_access_token(os.environ['TWITTER_ACCESS_KEY'],
                          os.environ['TWITTER_ACCESS_SECRET'])
    tweepy.API(auth)
    connect_msg = 'Connected to twitter with consumer key: {0}, {1} access_secret: *****'
    logging.info(__(connect_msg, os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_ACCESS_KEY']))
    logging.info(__('Using Location filter with bounding box of {0}', bounding))
    listener = CustomStreamListener(s3buffer, True)
    tweet_stream = tweepy.streaming.Stream(auth, listener)
    tweet_stream.filter(locations=bounding)

if __name__ == "__main__":
    LOG_STRING = "[%(asctime)s] %(levelname)s %(name)s:%(funcName)s:%(lineno)s - %(message)s"
    logging.basicConfig(format=LOG_STRING, level=logging.INFO)
    run()
