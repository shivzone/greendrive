import slack

class SlackNotification:

    def __init__(self, token, channel, debug=False):
        self.slackAPIToken = token
        self.slackChannel = channel
        self.debug = debug

    def sendMessage(self, message):
        if self.debug:
            return
        client = slack.WebClient(token=self.slackAPIToken )
        response = client.chat_postMessage(
            channel=self.slackChannel,
            text=message
        )
