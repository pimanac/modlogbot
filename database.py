import mysql.connector
import json
import sys
from datetime import datetime
from pprint import pprint
import inspect
from prawoauth2 import PrawOAuth2Mini as pmini
import praw

class database():

    REDDIT_ROOT = "http://www.reddit.com"


    def __init__(self):
        self.__config__()
        self.init = True

    def __config__(self):
        with open('config.json','r') as f:
            self.config = json.load(f);


    def connect(self):
        self.db = mysql.connector.connect(host=self.config['database']['host'],
                                          user=self.config['database']['user'],
                                          password=self.config['database']['password'],
                                          database='modlog')

    def get_submission(self,link):
        return self.r.get_submission(REDDIT_ROOT + link)

    def insert_comment(self,comment):
        sql = (
           "INSERT INTO comments (approved_by, archived, author, author_flair_css_class, author_flair_text, "
           "                     banned_by, body, body_html, controversiality, created, created_utc, distinguished, "
           "                     downs, edited, fetched, fullname, gilded, has_fetched, id, is_root, likes, link_author, "
           "                     link_id, link_title, link_url, name, num_reports, over_18, parent_id, permalink, "
           "                     quarantine, removal_reason, saved, score, score_hidden, stickied, subreddit_id, subreddit, "
           "                     ups) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
           "                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);" #39 fields
        )

        if comment.approved_by is not None:
            approved_by = comment.approved_by.name
        else:
            approved_by = None

        archived = comment.archived

        author = comment.author.name
        author_flair_css_class = comment.author_flair_css_class
        author_flair_text = comment.author_flair_text
        banned_by = comment.banned_by
        body = comment.body
        body_html = comment.body_html
        controversiality = comment.controversiality
        created = datetime.fromtimestamp(comment.created)
        created_utc = datetime.fromtimestamp(comment.created_utc)
        distinguished = comment.distinguished
        downs = comment.downs
        edited = comment.edited
        fetched = ""
        fullname = comment.fullname
        gilded = comment.gilded
        has_fetched = comment.has_fetched
        rid = comment.id
        is_root = comment.is_root
        likes = comment.likes
        link_author = comment.link_author
        link_id = comment.link_id
        link_title = comment.link_title
        link_url = comment.link_url
        name = comment.name
        num_reports = comment.num_reports
        over_18 = comment.over_18
        parent_id = comment.parent_id
        permalink = comment.permalink
        quarantine = comment.quarantine
        removal_reason = comment.removal_reason
        saved = comment.saved
        score = comment.score
        score_hidden = comment.score_hidden
        stickied = comment.stickied
        subreddit_id = comment.subreddit_id
        subreddit = comment.subreddit.name
        ups = comment.ups

        data = (
            approved_by,
            archived,
            author,
            author_flair_css_class,
            author_flair_text,
            banned_by,
            body,
            body_html,
            controversiality,
            created,
            created_utc,
            distinguished,
            downs,
            edited,
            fetched,
            fullname,
            gilded,
            has_fetched,
            rid,
            is_root,
            likes,
            link_author,
            link_id,
            link_title,
            link_url,
            name,
            num_reports,
            over_18,
            parent_id,
            permalink,
            quarantine,
            removal_reason,
            saved,
            score,
            score_hidden,
            stickied,
            subreddit_id,
            subreddit,
            ups
        )

        #pprint(data)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql,data)
            self.db.commit()
            cursor.close()
            print("\033[94m" + "inserted " + name + "\033[0m")
        except mysql.connector.Error as err:
            print (err)
            if err.errno == 1062:
                print("\033[92m" + "skipping " + name + "\033[0m")
            else:
                pass
    # insert_comment

    def insert_modlog(self, entry):
        cursor = self.db.cursor()

        action = entry.action or ""
        created = datetime.fromtimestamp(entry.created_utc)
        description = entry.description or ""
        details = entry.details or ""
        fullname = entry.target_fullname or ""
        has_fetched = True # this is being deprecated in PRAW4
        id = entry.id or ""
        mod = entry.mod or ""
        mod_id36 = entry.mod_id36 or ""
        rs_id36 = entry.sr_id36 or ""
        target_author = entry.target_author or ""
        target_fullname = entry.target_fullname or ""
        target_permalink = entry.target_permalink or ""


        sql = (
           "INSERT INTO modlog (action,created,description,details,fullname,has_fetched,id,"
           "                      moderator,mod_id36,rs_id36,target_author,target_fullname,target_permalink)"
           "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        )

        data = (action,
                created,
                description,
                details,
                fullname,
                has_fetched,
                id,
                mod,
                mod_id36,
                rs_id36,
                target_author,
                target_fullname,
                target_permalink
        )

        try:
            cursor.execute(sql,data)
            self.db.commit()
            cursor.close()
            print("\033[94m" + "inserted " + target_fullname + "\033[0m")
            return True
        except mysql.connector.Error as err:
            print (err)
            if err.errno == 1062:
                print("\033[92m" + "skipping " + target_fullname + "\033[0m")
                return False
            else:
                pass

    def insert_submission(self,submission):



        '''
         ('approved_by', None),
         ('archived', False),
         ('author', Redditor(user_name='FallenMan')),
         ('author_flair_css_class', None),
         ('author_flair_text', None),
         ('banned_by', None),
         ('clicked', False),
         ('created', 1454817222.0),
         ('created_utc', 1454788422.0),
         ('distinguished', None),
         ('domain', u'self.politics'),
         ('downs', 0),
         ('edited', 1454789059.0),
         ('from', None),
         ('from_id', None),
         ('from_kind', None),
         ('fullname', u't3_44ht76'),
         ('gilded', 0),
         ('has_fetched', True),
         ('hidden', False),
         ('hide_score', False),
         ('id', u'44ht76'),
         ('is_self', True),
         ('json_dict', None),
         ('likes', None),
         ('link_flair_css_class', None),
         ('link_flair_text', None),
         ('locked', False),
         ('name', u't3_44ht76'),
         ('num_comments', 21),
         ('num_reports', 0),
         ('over_18', False),
         ('permalink',
          u'https://www.reddit.com/r/politics/comments/44ht76/third_way_democrats/'),
         ('post_hint', u'self'),
         ('quarantine', False),
         ('removal_reason', None),
         ('report_reasons', []),
         ('saved', False),
         ('score', 0),
         ('secure_media', None),
         ('secure_media_embed', {}),
         ('selftext',
          u"https://medium.com/@matthewstoller/its-al-froms-democratic-party-we-just-live-here-5d0de7f89c3e#.spy0lbive\n\nFor anyone interested in a historical explanation of what's been going on during these primaries.\n\nITT: People who did not read the post and responded to the title -___-"),
         ('selftext_html',
          u'<!-- SC_OFF --><div class="md"><p><a href="https://medium.com/@matthewstoller/its-al-froms-democratic-party-we-just-live-here-5d0de7f89c3e#.spy0lbive">https://medium.com/@matthewstoller/its-al-froms-democratic-party-we-just-live-here-5d0de7f89c3e#.spy0lbive</a></p>\n\n<p>For anyone interested in a historical explanation of what&#39;s been going on during these primaries.</p>\n\n<p>ITT: People who did not read the post and responded to the title -___-</p>\n</div><!-- SC_ON -->'),
         ('short_link', u'http://redd.it/44ht76'),
         ('stickied', False),
         ('subreddit', Subreddit(subreddit_name='politics')),
         ('subreddit_id', u't5_2cneq'),
         ('suggested_sort', None),
         ('thumbnail', u'self'),
         ('title', u'Third Way Democrats'),
         ('ups', 0),
         ('url',
          u'https://www.reddit.com/r/politics/comments/44ht76/third_way_democrats/'),
         ('user_reports', []),
         ('visited', False),
        '''
        cursor = self.db.cursor()

        # 30 fields
        sql = (
           "INSERT INTO submissions (approved_by, archived, author, author_flair_css_class, "
           "                         author_flair_text, banned_by, clicked, created, created_utc, distinguished, "
           "                         domain, downs, edited, rfrom, from_id, from_kind, fullname, gilded, has_fetched, "
           "                         hidden, hide_score, id, is_self, likes, link_flair_css_class, link_flair_text, "
           "                         locked, name, over_18, permalink, post_hint, quarantine, removal_reason, "
           "                         saved, score, selftext, selftext_html, short_link, stickied, subreddit, "
           "                         subreddit_id, title, ups, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
           "                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
           "                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" # there should be 29 fields
        )
        # pprint(inspect.getmembers(submission.author))

        if submission.approved_by is not None:
            approved_by = submission.approved_by.name
        else:
            approved_by = None

        archived = submission.archived

        if submission.author is not None:
           author = submission.author.name
        else:
           author = ""

        author_flair_css_class = submission.author_flair_css_class
        author_flair_text = submission.author_flair_text

        if submission.banned_by is not None:
            banned_by = submission.banned_by.name
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
'''
    def load_submissions(self):
        cursor = self.db.cursor(buffered=True)

        sql = "SELECT distinct(target_permalink) FROM `modlog` where target_fullname like 't3_%';"

        cursor.execute(sql)
        items = []

        rows = cursor.fetchall()

        i = 1
        for row in rows:
            self.insert_submission(self.r.get_submission('http://www.reddit.com' + row[0]))

            if i == 100:
                print("got 100 - inserting")
                for submission in self.r.get_submissions(items):
                    self.insert_submission(submission)
                    items = []

            items += row[0]
            i += 1
'''
