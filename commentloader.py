#!/usr/bin/env python
import os
import collections
import praw
import json
import mysql.connector
from prawoauth2 import PrawOAuth2Mini as pmini
from database import database

class commentloader(object):

    def __init__(self):
        print("Comment Loader Starting")
        self.__config__()

    def __config__(self):
        with open('config.json','r') as f:
            self.config = json.load(f);

    def reddit_connect(self):
        ''' Connects to Reddit API '''

        self.r = praw.Reddit('pimanac log analysis')
        scope_list = ['read', 'modlog', 'privatemessages', 'submit']
        self.oauth = pmini(self.r, app_key=self.config['reddit']['key'],
                           app_secret=self.config['reddit']['secret'],
                           access_token=self.config['reddit']['access_token'],
                           refresh_token=self.config['reddit']['refresh_token'],
                           scopes=scope_list)

        self.subreddit = self.r.get_subreddit(self.config['reddit']['subreddit'])

    def load_comments_live(self):
        self.db = database()
        self.db.connect()
        for comment in praw.helpers.comment_stream(self.r, self.config['reddit']['subreddit'],
                                           limit=20, verbosity=2):

           self.db.insert_comment(comment)

# entry
if __name__ == "__main__":
    me = commentloader()
    me.reddit_connect()

    while True:
        try:
           print("Getting live comment stream")
           me.load_comments_live()
        except:
           print("error.  sleeping 60 seconds")
           time.sleep(60)

    print("Exiting")
