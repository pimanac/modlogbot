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

    def insert_submission(self,submission):
        cursor = self.db.cursor()

        sql = (
           "INSERT INTO submissions (approved_by, archived, author, author_flair_css_class, "
           "                         author_flair_text, banned_by, clicked, created, created_utc, distinguished, "
           "                         domain, downs, edited, rfrom, from_id, from_kind, fullname, gilded, has_fetched, "
           "                         hidden, hide_score, id, is_self, likes, link_flair_css_class, link_flair_text, "
           "                         locked, name, over_18, permalink, post_hint, quarantine, removal_reason, "
           "                         saved, score, selftext, selftext_html, short_link, stickied, subreddit, "
           "                         subreddit_id, title, ups, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
           "                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
           "                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        if submission.approved_by is not None:
            approved_by = submission.approved_by.name
        else:
            approved_by = None

        archived = submission.archived
        if submission.author is not None:
            author = submission.author.name
        else:
            author = ''

        author_flair_css_class = submission.author_flair_css_class
        author_flair_text = submission.author_flair_text
        if submission.banned_by is not None:
           try:
              banned_by = submission.banned_by.name
           except:
              banned_by = ""
        else:
            banned_by = None

        clicked = True
        created = datetime.fromtimestamp(submission.created)
        created_utc = datetime.fromtimestamp(submission.created_utc)
        distinguished = submission.distinguished
        domain = submission.domain
        downs = submission.downs
        edited = submission.edited
        rfrom = ""
        from_id = submission.from_id
        from_kind = submission.from_kind
        fullanme = submission.fullname
        gilded = submission.gilded
        has_feteched = True
        hidden = submission.hidden
        hide_score = submission.hide_score
        rid = submission.id
        is_self = submission.is_self
        likes = submission.likes
        link_flair_css_class = submission.link_flair_css_class
        link_flair_text = submission.link_flair_text
        locked = submission.locked
        name = submission.name
        over_18 = submission.over_18
        permalink = submission.permalink
        post_hint = ""
        quarantine = submission.quarantine
        removal_reason = submission.removal_reason
        saved = submission.saved
        score = submission.score
        selftext = submission.selftext
        selftext_html = submission.selftext_html
        short_link = submission.short_link
        stickied = submission.stickied
        subreddit = submission.subreddit.name
        subreddit_id = submission.subreddit_id
        title = submission.title
        ups = submission.ups
        url = submission.url

        data = (
            approved_by,
            archived,
            author,
            author_flair_css_class,
            author_flair_text,
            banned_by,
            clicked,
            created,
            created_utc,
            distinguished,
            domain,
            downs,
            edited,
            rfrom,
            from_id,
            from_kind,
            fullanme,
            gilded,
            has_feteched,
            hidden,
            hide_score,
            rid,
            is_self,
            likes,
            link_flair_css_class,
            link_flair_text,
            locked,
            name,
            over_18,
            permalink,
            post_hint,
            quarantine,
            removal_reason,
            saved,
            score,
            selftext,
            selftext_html,
            short_link,
            stickied,
            subreddit,
            subreddit_id,
            title,
            ups,
            url
        )

        try:
            cursor.execute(sql,data)
            self.db.commit()
            cursor.close()
            print("\033[94m" + "inserted " + title + "\033[0m")
        except mysql.connector.Error as err:
            print (err)
            if err.errno == 1062:
                print("\033[92m" + "skipping " + title + "\033[0m")
            else:
                pass
    # InsertSubmission

    def load_submissions(self):
        cursor = self.db.cursor()
        query = "SELECT DISTINCT(target_permalink) FROM modlog WHERE target_fullname NOT IN (SELECT fullname as target_fullname FROM submissions) AND target_permalink != '' AND (action = 'approvelink' or action = 'removelink') ORDER BY created DESC;"

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            link = 'https://www.reddit.com' + row[0]
            print("getting " + link)
            submission = self.r.get_submission(link)

            self.insert_submission(submission)

# entry
if __name__ == "__main__":
    me = submissionloader()
    me.reddit_connect()

    while True:
        print("Getting back submissions")
        me.load_submissions()

    print("Exiting")
