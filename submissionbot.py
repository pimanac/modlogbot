#!/usr/bin/env python
import os
import sys
import collections
import praw
import json
import mysql.connector
from prawoauth2 import PrawOAuth2Mini as pmini
from database import database
import time
import yaml

from pprint import pprint
import inspect

class bcolors:
   HEADER = '\033[95m'
   OKBLUE = '\033[94m'
   OKGREEN = '\033[92m'
   WARNING = '\033[93m'
   FAIL = '\033[91m'
   ENDC = '\033[0m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'

class submissionloader(object):

    def __init__(self):
        print("Submission bot Starting")
        self.done = []
        self.__config__()

    def __config__(self):
        with open('config.json','r') as f:
            self.config = json.load(f);
            
    def wiki_config(self):
       # load subreddit config from wiki
       try:
          wiki = self.subreddit.get_wiki_page('modlogbot').content_md
          self.subconfig = yaml.load(wiki)
       except Exception as e:
          print("invalid wiki yaml")
          print(str(e))
          sys.exit()

    def reddit_connect(self):
        ''' Connects to Reddit API '''

        self.r = praw.Reddit('pimanac log analysis')
        scope_list = ['modflair','identity','modposts','read','submit','wikiread','modwiki','report','edit','flair','modlog']
        self.oauth = pmini(self.r, app_key=self.config['reddit']['key'],
                           app_secret=self.config['reddit']['secret'],
                           access_token=self.config['reddit']['access_token'],
                           refresh_token=self.config['reddit']['refresh_token'],
                           scopes=scope_list)

        self.subreddit = self.r.get_subreddit(self.config['reddit']['subreddit'])
        self.user = self.r.get_me()
        self.wiki_config()

    def load_submissions_live(self):
        self.db = database()
        self.db.connect()
        #for submission in praw.helpers.submission_stream(self.r, self.config['reddit']['subreddit'],
        #                                   limit=500, verbosity=2):
        for submission in self.subreddit.get_unmoderated(limit=1000):
        
           if submission.fullname in self.done:
              continue
              
           try:
              self.db.insert_submission(submission)
              print("inserting")
           except:
              print(bcolors.FAIL + "Unable to insert submission " + submission.fullname + bcolors.ENDC)
              continue
              
           if submission.approved_by is not None:
              continue
              
           # flood protection
           print("flood detection...")
           self.flood_protection(submission)
           
           print("max sumbission...")
           self.max_submissions(submission)
           
           self.done += submission.fullname
           time.sleep(0.5)
         
    def max_submissions(self,submission):
       # if it has a link its been actioned.

       if submission.link_flair_text is not None:
          return
          
       if submission.link_flair_text == "":
          return
          
          
       try:
          data = self.db.check_submissions_per_day(submission)
       except Exception as e:
          print(bcolors.FAIL + "Unable to get number of submissions per day"  + bcolors.ENDC)
          print(str(e))
          #sys.exit()
          return
          
       limit = int(self.subconfig['flood_protection']['max_submissions_per_day'])
       flair = str(self.subconfig['flood_protection']['flair'])
       comment = str(self.subconfig['flood_protection']['max_submissions_per_day_comment'])
       
       cnt = data['submissions']
       
       if cnt > 0 and cnt >= limit:
            print(bcolors.WARNING + "User reached submission limit" + bcolors.ENDC)
            try:
               print("reporting")
               # submission.report('Flood warning: user has max daily submissions' )
               
               print("setting flair to : " + flair)
               self.subreddit.set_flair(submission,flair,None)
               
               print("removing")
               submission.remove()
               
               print("commenting and distinguishing")
               
               # build the table of links
               stuff = "You have already submitted " + str(limit) + " articles within the last 24 hours. These links are:\r\n\r\n"
               # because we dont want to include this post itself.
               for i in range(0,limit):
                  stuff += "* [" + data['titles'][i] + "](" + data['links'][i] + ")\r\n\r\n"
               
               comment = comment.replace('[AUTHOR]',submission.author.name)
               comment = comment.replace('[LINKLIST]',stuff)
               
               print("comment is")
               print("~"*20)
               print(comment)
               print("~"*20)
               
               submission.add_comment(comment).distinguish()
               #sys.exit()
            except Exception as e:
               print(str(e))
               return
       else:
            print(bcolors.OKBLUE + "Submission is Ok" + bcolors.ENDC)
       
    def flood_protection(self,submission):
         # time between posts
         try:
            data = self.db.check_time_between_submissions(submission)
         except Exception as e:
            print(bcolors.FAIL + "Unable to get time between last submission"  + bcolors.ENDC)
            print(str(e))
            return
         
         limit = int(self.subconfig['flood_protection']['min_wait_between_submissions'])
         flair = str(self.subconfig['flood_protection']['flair'])
         comment = str(self.subconfig['flood_protection']['min_wait_between_submissions_comment'])

         age = data['minutes']

         if age > 0 and age < limit:
            print(bcolors.WARNING + "TIME SINCE LAST < 10 minutes | " + data['prev_short_link'] + bcolors.ENDC)
            try:
               print("reporting")
               # submission.report('Flood warning: last submission < 10 minutes ago  | ' + str(data['prev_short_link']) )
               
               print("setting flair to : " + flair)
               self.subreddit.set_flair(submission,flair,None)
               
               print("removing")
               submission.remove()

               print("commenting and distinguishing")
               
               comment = comment.replace('[AUTHOR]',submission.author.name)
               comment = comment.replace('[LINKLIST]',data['prev_short_link'])
               
               print("comment is")
               print("~"*20)
               print(comment)
               print("~"*20)
               
               submission.add_comment(comment).distinguish()
               #sys.exit()
            except Exception as e:
               print(bcolors.FAIL + "unable to report submission" + bcolors.ENDC)
               print(str(e))
               return
         else:
            print(bcolors.OKBLUE + "Submission is Ok" + bcolors.ENDC)
            
            
# entry
if __name__ == "__main__":
   me = submissionloader()
   me.reddit_connect()
   doit = True
   while doit:
      me.wiki_config()
      me.load_submissions_live()
      sleep(60*5)
   print("Exiting")
