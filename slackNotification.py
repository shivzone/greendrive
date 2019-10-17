import os
import slack

class SlackNotification:
    slackAPIToken = "xoxb-2156835366-798368800885-FUlo3ktuPtZMtl80pvjTL0cF"
    slackChannel = "#dpm-members"

    def sendMessage(self, message):
        client = slack.WebClient(token=slackAPIToken )
        response = client.chat_postMessage(
            channel=self.channel
            text=message
        print(response)