#!/usr/bin/env python
import os
import collections
import praw
import json
import mysql.connector
import time
from prawoauth2 import PrawOAuth2Mini as pmini
from database import database

from pprint import pprint
import inspect

class submissionloader(object):

    def __init__(self):
        print("Submission Loader Starting")
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

    def load_submissions_live(self):
        self.db = database()
        self.db.connect()
        for submission in praw.helpers.submission_stream(self.r, self.config['reddit']['subreddit'],
                                           limit=None, verbosity=2):
        #for submission in self.subreddit.get_submissions():
           self.db.insert_submission(submission)

# entry
if __name__ == "__main__":
   me = submissionloader()
   me.reddit_connect()

   while True:
      try:
         print("Getting live submission stream")
         me.load_submissions_live()
      except:
         print("error.  Sleeping 60 seconds.")
         time.sleep(60)

   print("Exiting")
