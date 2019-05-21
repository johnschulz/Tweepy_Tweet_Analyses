from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import twitter_credentials
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt


class TwitterClient():
    def __init__(self, twitter_user = None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth
class TwitterStreamer():

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweet_filename, hash_tag_list):
        listener = TwitterListener(fetched_tweet_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track = hash_tag_list)

class TwitterListener(StreamListener):
    def __init__(self,fetched_tweet_filename):
        self.fetched_tweet_filename = fetched_tweet_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweet_filename, "a") as tf:
                tf.write(data)
            return True
        except Exception as e:
            print("Error on data: %s" % str(e))
        return True
    def on_error(self, status):
        if status == '420':
            return False
        print(status)
class TweetAnalyzer():
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data =[tweet.favorite_count for tweet in tweets], columns= ['Likes'])
        df['Date'] = np.array([tweet.created_at for tweet in tweets])
        df['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['Text'] = np.array([tweet.text[0:2] for tweet in tweets])
        df['Retweeted'] = np.array([tweet.user for tweet in tweets])
        return df
    # def clean_tweet(self, tweet):
    #     return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    # def analyze_sentiment(self, tweet):
    #     analysis = TextBlob(self.clean_tweet(tweet))
    #     if analysis.sentiment.polarity > 0:
    #         return 1
    #     elif analysis.sentiment.polarity == 0:
    #         return 0
    #     else:
    #         return -1


if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name = 'realDonaldTrump', count = 250)
    
    #
    #
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    # df['Sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Text']])






    """all the possible categories to look into"""
    # print(dir(tweets[0]))
    """get first ten elements"""
    print(df.head(250))
    """get average"""
    # print(np.mean(df['Likes']))
    """Most liked tweet"""
    # print(np.max(df['Likes']))

    """Time Series"""
    time_likes = pd.Series(data=df["Likes"].values, index=df['Date'])
    time_likes.plot(figsize=(16,4), color = 'r', label = 'Likes', legend=True)
    time_retweets = pd.Series(data=df["Retweets"].values, index=df['Date'])
    time_retweets.plot(figsize=(16,4), color = 'b', label = 'Retweets', legend=True)
    plt.show()


    # fetched_tweet_filename = "tweets.txt"
    #
    # twitter_client = TwitterClient('realDonaldTrump')
    # print(twitter_client.get_user_timeline_tweets(1))
    #
    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(fetched_tweet_filename, hash_tag_list)
