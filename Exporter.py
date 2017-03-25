# -*- coding: utf-8 -*-
import sys
import getopt
import codecs
import got3 as got


def main(argv):

    if len(argv) == 0:
        print('You must pass some parameters. Use \"-h\" to help.')
        return

    if len(argv) == 1 and argv[0] == '-h':
        print("""\nTo use this jar, you can pass the folowing attributes:
    username: Username of a specific twitter account (without @)
       since: The lower bound date (yyyy-mm-aa)
       until: The upper bound date (yyyy-mm-aa)
 querysearch: A query text to be matched
   maxtweets: The maximum number of tweets to retrieve
    filename: Enter a name for the file where the tweets are stored
min_retweets: Enter the number of minimum retweets
   min_faves: Enter the number of minimum faves for tweets with youtube vids

 \nExamples:
 # Example 1 - Get tweets by username [barackobama]
 python Exporter.py --username "barackobama" --maxtweets 1\n

 # Example 2 - Get tweets by query search [europe refugees]
 python Exporter.py --querysearch "europe refugees" --maxtweets 1\n

 # Example 3 - Get tweets by username and bound dates [barackobama,
 '2015-09-10', '2015-09-12']
 python Exporter.py --username "barackobama" --since 2015-09-10 --until
 2015-09-12 --maxtweets 1\n

 # Example 4 - Get the last 10 top tweets by username
 python Exporter.py --username "barackobama" --maxtweets 10 --toptweets\n""")
        return

    try:
        opts, args = getopt.getopt(
            argv, '', ('username=', 'near=', 'within=', 'since=', 'until=',
                       'querysearch=', 'toptweets', 'maxtweets=', 'filename=',
                       'mode=', 'min_retweets=', 'min_faves='))

        tweetCriteria = got.manager.TweetCriteria()

        # Add default value for mode
        mode = 'w+'
        for opt, arg in opts:
            if opt == '--username':
                tweetCriteria.username = arg

            elif opt == '--since':
                tweetCriteria.since = arg

            elif opt == '--until':
                tweetCriteria.until = arg

            elif opt == '--querysearch':
                tweetCriteria.querySearch = arg

            elif opt == '--toptweets':
                tweetCriteria.topTweets = True

            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)

            elif opt == '--near':
                tweetCriteria.near = '"' + arg + '"'

            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'

            elif opt == '--filename':
                filename = arg

            elif opt == '--mode':
                mode = arg

            elif opt == '--min_retweets':
                tweetCriteria.min_retweets = arg

            elif opt == '--min_faves':
                tweetCriteria.min_faves = arg

        outputFile = codecs.open("{}.csv".format(filename), mode, "utf-8")

        outputFile.write(
            'username;date;retweets;favorites;text;geo;mentions;hashtags;id'
            ';permalink')

        print('Searching...')

        def receiveBuffer(tweets):
            for t in tweets:
                outputFile.write((
                    '\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s' % (
                        t.username, t.date.strftime("%Y-%m-%d %H:%M"),
                        t.retweets, t.favorites, t.text, t.geo, t.mentions,
                        t.hashtags, t.id, t.permalink)))
            outputFile.flush()

        got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)

    except arg:
        print('Arguments parser error, try -h' + arg)
    finally:
        outputFile.close()
        print('Done. Output file generated "{}.csv".'.format(filename))


if __name__ == '__main__':
    main(sys.argv[1:])
