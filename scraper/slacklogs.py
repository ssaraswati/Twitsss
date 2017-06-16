import config as cfg
import json
import requests

class SlackLogs(object):
    webhook_url = cfg.slack['logsurl']

    def send(self, text, name=None, icon=None, channel=None):
        if name == None:
            name = "logbot"
        if channel == None:
            channel = "#logs"
        if icon == None:
            icon = ":hatched_chick:"

        slack_data = {"channel": channel, 'text': text, "icon_emoji": icon, "username": name}

        response = requests.post(
            self.webhook_url, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )