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

        self.r = praw.Reddit('Fetching mod-related info for IRC')
        scope_list = ['read', 'modlog', 'privatemessages', 'submit']
        self.oauth = pmini(self.r, app_key=self.config['reddit']['key'],
                           app_secret=self.config['reddit']['secret'],
                           access_token=self.config['reddit']['access_token'],
                           refresh_token=self.config['reddit']['refresh_token'],
                           scopes=scope_list)

        self.subreddit = self.r.get_subreddit(self.config['reddit']['subreddit'])
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
        cursor = self.db.cursor()

        # 30 fields
        sql = (
           "INSERT INTO submission (author,banned_by,created_utc,distinguished,"
           "domain,downs,edited,rfrom,from_id,from_kind,gilded,hidden,hide_score,"
           "id,is_self,link_flair_css_class,link_flair_text,locked,media,name,permalink,"
           "post_hint,quarantine,removal_reason,subreddit_id,title,ups,upvote_ratio,url,self_text) "
           "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
           "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" # there should be 29 fields
        )
        # pprint(inspect.getmembers(submission.author))
        author = submission.author.name or ""
        banned_by = submission.banned_by or ""
        created_utc = datetime.fromtimestamp(submission.created_utc)
        distinguished = submission.distinguished or False
        domain = submission.domain or ""
        downs = submission.downs or 0
        edited = submission.edited or False
        # rfrom = submission.from or ""
        rfrom = ""
        from_id = submission.from_id or ""
        from_kind = submission.from_kind or ""
        gilded = submission.gilded or 0
        hidden = submission.hidden or False
        hide_score = submission.hide_score or False
        rid = submission.id or ""
        is_self = submission.is_self or False
        link_flair_css_class = submission.link_flair_css_class or ""
        link_flair_text = submission.link_flair_text or ""
        locked = submission.locked or False
        media = submission.media or ""
        name = submission.name or ""
        permalink = submission.permalink or ""
        post_hint = submission.post_hint or ""
        quarantine = submission.quarantine or False
        removal_reason = submission.removal_reason or ""
        subreddit_id = submission.subreddit_id or ""
        title = submission.title or ""
        ups = submission.ups or 0
        upvote_ratio = submission.upvote_ratio or 0.00
        url = submission.url or ""

        selftext = submission.selftext or ""

        data = (author,
                banned_by,
                created_utc,
                distinguished,
                domain,
                downs,
                edited,
                rfrom,
                from_id,
                from_kind,
                gilded,
                hidden,
                hide_score,
                rid,
                is_self,
                link_flair_css_class,
                link_flair_text,
                locked,
                media,
                name,
                permalink,
                post_hint,
                quarantine,
                removal_reason,
                subreddit_id,
                title,
                ups,
                upvote_ratio,
                url,
                selftext
        )

        pprint(data)
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
        cursor = self.db.cursor(buffered=True)

        sql = "SELECT target_permalink FROM modlog WHERE action = 'approvelink' or action = 'removelink';"

        cursor.execute(sql)

        for target_permalink in cursor:
            print(target_permalink)

            item = self.get_submission(self.config['reddit']['root'] + target_permalink)
            self.insert_submission(item)
