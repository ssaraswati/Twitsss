import tinys3
import config as cfg
from slacklogs import SlackLogs


class S3up(object):

    def __init__(self, bucket):
        self.bucket = bucket

    @staticmethod
    def send_logs_slack(message):
        log = SlackLogs()
        log.send(message, "s3scrapeupload", ":floppy_disk:", "scrapelogs")

    def upload(self, body, key):

        conn = tinys3.Connection(cfg.aws['access_key'], cfg.aws['access_secret_key'], tls=True)
        conn.upload(key, body, self.bucket)
