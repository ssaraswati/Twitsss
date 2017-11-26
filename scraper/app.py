import sys,os,json,datetime,time
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
        print('Tweets in buffer(' + str(tweets_in_buffer) + ')Latest:' + tweet['text'] + 'id:'+ tweet['id_str'])
        if (tweets_in_buffer >= cfg.buffersize):
            self.upload_now()

    def upload_now(self):
        print('Saving to s3')
        key = str(int(time.time())) + '.json'
        self.s3.Object(self.bucket_name, key).put(Body=json.dumps(self.tweets), Metadata={'Content-Type': 'application/json'})
        self.tweets = [] 
        

class CustomStreamListener(tweepy.StreamListener):

    def setup_datastore(self, datastore):
        self.datastore = datastore

    def on_status(self, status):
        if self.datastore is None:
            print('Nothing to do with tweets no datastore...Exiting', file=sys.stderr)
            exit
        if not cfg.geo_only:
            self.datastore.add_tweet(status._json)
        elif cfg.geo_only and status._json['coordinates'] is not None:
            self.datastore.add_tweet(status._json)

    def on_error(self, status_code):
        print('Encountered error with status code:', status_code, file=sys.stderr)
        return True # Don't kill the stream

    def on_timeout(self):
        print('Timeout...', file=sys.stderr)
        return True # Don't kill the stream

def run():
    print('Starting tweet to s3 stream scraper @ {0}'.format(str(datetime.datetime.now())))

    s3buffer = AWSS3UploadBuffer(cfg.aws['access_key'], cfg.aws['access_secret_key'], cfg.aws['region'], cfg.aws['bucket'])
    #Connect to twitter
    auth = tweepy.OAuthHandler(cfg.twitter['consumer_key'], cfg.twitter['consumer_secret'])
    auth.set_access_token(cfg.twitter['access_key'], cfg.twitter['access_secret'])
    api = tweepy.API(auth)
    print('Connected to twitter with consumer key: {0} consumer secret:***** access key:{1} access_secret:*****'.format(cfg.twitter['consumer_key'], cfg.twitter['access_key']))

    print('Using Location filter with bounding box of {0}'.format(str(cfg.boundingBox)))
    listener = CustomStreamListener()
    listener.setup_datastore(s3buffer)
    tweet_stream = tweepy.streaming.Stream(auth, listener)
    tweet_stream.filter(locations=cfg.boundingBox)
    

if __name__ == "__main__":
    run()
