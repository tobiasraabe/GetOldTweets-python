class TweetCriteria:

    def __init__(self):
        self.maxTweets = 0

    def setUsername(self, username):
        self.username = username
        return self

    def setSince(self, since):
        self.since = since
        return self

    def setUntil(self, until):
        self.until = until
        return self

    def setQuerySearch(self, querySearch):
        self.querySearch = querySearch
        return self

    def setMaxTweets(self, maxTweets):
        self.maxTweets = maxTweets
        return self

    def setLang(self, Lang):
        self.lang = Lang
        return self

    def setTopTweets(self, topTweets):
        self.topTweets = topTweets
        return self

    def set_min_retweets(self, min_retweets):
        self.min_retweets = min_retweets
        return self

    def set_min_faves(self, min_faves):
        self.min_faves = min_faves
        return self
