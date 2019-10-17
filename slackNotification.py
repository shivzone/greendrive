import slack

class SlackNotification:

    def __init__(self, token, channel):
        self.slackAPIToken = token
        self.slackChannel = channel

    def sendMessage(self, message):
        client = slack.WebClient(token=self.slackAPIToken )
        response = client.chat_postMessage(
            channel=self.slackChannel,
            text=message
        )
        print(response)
