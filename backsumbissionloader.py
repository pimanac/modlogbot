#!/usr/bin/env python
import os
import collections
import praw
import json
import mysql.connector
from prawoauth2 import PrawOAuth2Mini as pmini
from database import database
from datetime import datetime

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

        self.db = mysql.connector.connect(host=self.config['database']['host'],
                                          user=self.config['database']['user'],
                                          password=self.config['database']['password'],
                                          database='modlog')


    def load_submissions(self):
        cursor = self.db.cursor()
        query = "SELECT DISTINCT(target_permalink) FROM modlog WHERE target_fullname NOT IN (SELECT fullname as target_fullname FROM submissions) AND target_permalink != '' AND (action = 'approvelink' or action = 'removelink') ORDER BY created DESC;"

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            link = 'https://www.reddit.com' + row[0]
            # print("getting " + link)
            try:
               db = database()
               db.connect()
               submission = self.r.get_submission(link)
               db.insert_submission(submission)
            except:

               print("error getting submission " + link)
               raise
               #pass

# entry
if __name__ == "__main__":
    me = submissionloader()
    me.reddit_connect()

    while True:
        print("Getting back submissions")
        me.load_submissions()
        print("sleeping")
        time.sleep(5 * 60)


    print("Exiting")
