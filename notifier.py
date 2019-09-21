class Notifier(object):

    def __init__(self, channel, config):
        self.channel = channel
        self.config = config

    def match_keywords(self, deal):
        return True
