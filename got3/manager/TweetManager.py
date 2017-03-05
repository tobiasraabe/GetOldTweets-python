import datetime
import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from .. import models
from pyquery import PyQuery


class TweetManager:

    def __init__(self):
        pass

    @staticmethod
    def getTweets(tweetCriteria, receiveBuffer=None, bufferLength=100):
        os.environ['GOT_COUNTER'] = '0'

        refreshCursor = ''

        results = []
        resultsAux = []
        cookieJar = http.cookiejar.CookieJar()

        active = True

        while active:
            json = TweetManager.getJsonReponse(
                tweetCriteria, refreshCursor, cookieJar)
            if len(json['items_html'].strip()) == 0:
                break

            refreshCursor = json['min_position']
            tweets = PyQuery(json['items_html'])('div.js-stream-tweet')

            if len(tweets) == 0:
                break

            os.environ['GOT_COUNTER'] = str(
                int(os.environ['GOT_COUNTER']) + len(tweets))

            for tweetHTML in tweets:
                tweetPQ = PyQuery(tweetHTML)
                tweet = models.Tweet()

                usernameTweet = tweetPQ(
                    "span.username.js-action-profile-name b").text()
                txt = re.sub(
                    r"\s+", " ", tweetPQ("p.js-tweet-text").text()
                    .replace('# ', '#').replace('@ ', '@'))
                rtwt = (
                    "span.ProfileTweet-action--retweet "
                    "span.ProfileTweet-actionCount")
                retweets = int(tweetPQ(rtwt).attr(
                    "data-tweet-stat-count").replace(",", ""))
                fvrt = (
                    "span.ProfileTweet-action--favorite "
                    "span.ProfileTweet-actionCount")
                favorites = int(tweetPQ(fvrt).attr(
                    "data-tweet-stat-count").replace(",", ""))
                dateSec = int(
                    tweetPQ("small.time span.js-short-timestamp")
                    .attr("data-time"))
                id = tweetPQ.attr("data-tweet-id")
                permalink = tweetPQ.attr("data-permalink-path")
                user_id = int(
                    tweetPQ("a.js-user-profile-link").attr("data-user-id"))

                geo = ''
                geoSpan = tweetPQ('span.Tweet-geo')
                if len(geoSpan) > 0:
                    geo = geoSpan.attr('title')
                urls = []
                for link in tweetPQ("a"):
                    try:
                        urls.append((link.attrib["data-expanded-url"]))
                    except KeyError:
                        pass
                tweet.id = id
                tweet.permalink = 'https://twitter.com' + permalink
                tweet.username = usernameTweet

                tweet.text = txt
                tweet.date = datetime.datetime.fromtimestamp(dateSec)
                tweet.formatted_date = datetime.datetime.fromtimestamp(
                    dateSec).strftime("%a %b %d %X +0000 %Y")
                tweet.retweets = retweets
                tweet.favorites = favorites
                tweet.mentions = " ".join(
                    re.compile('(@\\w*)').findall(tweet.text))
                tweet.hashtags = " ".join(
                    re.compile('(#\\w*)').findall(tweet.text))
                tweet.geo = geo
                tweet.urls = ",".join(urls)
                tweet.author_id = user_id

                results.append(tweet)
                resultsAux.append(tweet)

                if receiveBuffer and len(resultsAux) >= bufferLength:
                    receiveBuffer(resultsAux)
                    resultsAux = []

                if 0 < tweetCriteria.maxTweets <= len(results):
                    active = False
                    break

        if receiveBuffer and len(resultsAux) > 0:
            receiveBuffer(resultsAux)

        print('Collected {} tweets.'.format(
            os.environ.get('GOT_COUNTER', 'No response')))

        return results

    @staticmethod
    def getJsonReponse(tweetCriteria, refreshCursor, cookieJar):
        url = (
            "https://twitter.com/i/search/timeline?f=realtime&q=%s&src=typd"
            "&%smax_position=%s")

        urlGetData = ''
        if hasattr(tweetCriteria, 'username'):
            urlGetData += ' from:' + tweetCriteria.username

        if hasattr(tweetCriteria, 'since'):
            urlGetData += ' since:' + tweetCriteria.since

        if hasattr(tweetCriteria, 'until'):
            urlGetData += ' until:' + tweetCriteria.until

        if hasattr(tweetCriteria, 'querySearch'):
            urlGetData += ' ' + tweetCriteria.querySearch

        if hasattr(tweetCriteria, 'lang'):
            urlLang = 'lang=' + tweetCriteria.lang + '&'

        if hasattr(tweetCriteria, 'querySearch'):
            urlGetData += ' ' + tweetCriteria.querySearch

        if hasattr(tweetCriteria, 'near'):
            urlGetData += ("&near:" + tweetCriteria.near + " within:" +
                           tweetCriteria.within)

        else:
            urlLang = ''
        url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)

        headers = [
            ('Host', "twitter.com"),
            ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
            ('Accept', "application/json, text/javascript, */*; q=0.01"),
            ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
            ('X-Requested-With', "XMLHttpRequest"),
            ('Referer', url),
            ('Connection', "keep-alive")
        ]

        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookieJar))
        opener.addheaders = headers

        try:
            response = opener.open(url)
            jsonResponse = response.read()
        except:
            print(
                "Twitter weird response. Try to see on browser: "
                "https://twitter.com/search?q=%s&src=typd" %
                urllib.parse.quote(urlGetData))
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit()
            return

        dataJson = json.loads(jsonResponse.decode())

        return dataJson
