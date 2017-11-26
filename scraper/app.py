import sys,os,json,datetime,time,logging
import tweepy
import boto3
from boto3.session import Session
import config as cfg

class AWSS3UploadBuffer:
    tweets = [] 

    def __init__(self, aws_access_key_id, aws_secret_access_key, region, bucket_name):
        self.session = Session(aws_access_key_id=aws_access_key_id ,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name=region)
        self.s3 = self.session.resource("s3")
        self.bucket_name = bucket_name

    def add_tweet(self, tweet):
        self.tweets.append(tweet)
        tweets_in_buffer = len(self.tweets)
        logging.info('Tweets in buffer({0})Latest: {1} id: {2}', tweets_in_buffer, tweet['text'], tweet['id_str'])
        if (tweets_in_buffer >= cfg.buffersize):
            self.upload_now()

    def upload_now(self):
        key = str(int(time.time())) + '.json'
        self.s3.Object(self.bucket_name, key).put(Body=json.dumps(self.tweets), Metadata={'Content-Type': 'application/json'})
        logging.info('Saved {0} tweets to s3 bucket: {1} key: {2}', self.tweets, self.bucket_name, key))
        self.tweets = [] 
        

class CustomStreamListener(tweepy.StreamListener):
    def setup_datastore(self, datastore):
        self.datastore = datastore

    def on_status(self, status):
        if self.datastore is None:
            logging.critical('Nothing to do with tweets no datastore...Exiting')
            exit
        if not cfg.geo_only:
            self.datastore.add_tweet(status._json)
        elif cfg.geo_only and status._json['coordinates'] is not None:
            self.datastore.add_tweet(status._json)

    def on_error(self, status_code):
        logging.error('Encountered error with status code: {0}', status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        logging.error('Timeout...')
        return True # Don't kill the stream

def run():
    logging.info('Starting tweet to s3 streaming scraper @ {0}', datetime.datetime.now())

    s3buffer = AWSS3UploadBuffer(cfg.aws['access_key'], cfg.aws['access_secret_key'], cfg.aws['region'], cfg.aws['bucket'])
    auth = tweepy.OAuthHandler(cfg.twitter['consumer_key'], cfg.twitter['consumer_secret'])
    auth.set_access_token(cfg.twitter['access_key'], cfg.twitter['access_secret'])
    api = tweepy.API(auth)
    logging.info('Connected to twitter with consumer key: {0} consumer secret: ***** access key: {1} access_secret: *****', cfg.twitter['consumer_key'], cfg.twitter['access_key'])

    logging.info('Using Location filter with bounding box of {0}', cfg.boundingBox))
    listener = CustomStreamListener()
    listener.setup_datastore(s3buffer)
    tweet_stream = tweepy.streaming.Stream(auth, listener)
    tweet_stream.filter(locations=cfg.boundingBox)
    

if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] %(process)d %(levelname)s %(name)s:%(funcName)s:%(lineno)s - %(message)s",level=logging.INFO)
    loginfo_string = 'Log level enabled'
    logging.debug(loginfo_string)
    logging.info(loginfo_string)
    logging.warning(loginfo_string)
    logging.error(loginfo_string)
    logging.critical(loginfo_string)
    run()
