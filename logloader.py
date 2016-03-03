#!/usr/bin/env python
import os
import time
import collections
import praw
import json
import mysql.connector
from prawoauth2 import PrawOAuth2Mini as pmini
from pprint import pprint
from database import database

class logloader(object):

    def __init__(self):
        print("Starting")
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

    def get_submission(self,id):
        return self.r.get_submission(submission_id=id)
    # get_selfpost
    
    

    def get_modlog(self):
        db = database()
        db.connect()

        i=0
        exitAt = 100
        for x in self.subreddit.get_mod_log(limit=int(self.config['reddit']['max_requests'])):
            if x is not None:
                result = db.insert_modlog(x)
                type = x.target_fullname.split('_')[0]
                id = x.target_fullname.split('_')[1]
                
                if type == 't3':
                   db.insert_submission(self.get_submission(id))

                if result == False:
                    i += 1
                if i == exitAt:
                    print('OK Ive had enough')
                    break
            # end if


# entry
if __name__ == "__main__":
    with open('config.json','r') as f:
        config = json.load(f);
    me = logloader()
    me.reddit_connect()
    
    while True:
        print("Getting modlog")
        me.get_modlog()
        print("Sleeping...")
        time.sleep(int(config['reddit']['sleep_seconds']))

    print("Exiting")
