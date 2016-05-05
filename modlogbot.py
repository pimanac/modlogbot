#!/usr/bin/env python

import os
import re
import time
import socket
import collections
import mysql.connector
import json
import cgi
import urllib
from slackclient import SlackClient
from pprint import pprint
import inspect
from database import database
try:
   from http.server import BaseHTTPRequestHandler, HTTPServer
except:
   from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class bot(object):
   def __init__(self):
      self.__config__()
      self.enabled=True

   def __config__(self):
      with open('config.json','r') as f:
         self.config = json.load(f);

   def slack_connect(self):
      self.slack = SlackClient(self.config['slack']['bot_token'])
      try:
         self.slack.rtm_connect()
         print("connected")
      except:
         print("didn't connect to slack")
         
   def get_bots(self):

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']
      data['attachments'] = []
      
      text = '*Status of pim bots*\n'

       
      pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
      
      modlogbot = 'Running'
      datebot = 'NOT RUNNING'
      submissionLoader = 'NOT RUNNING'
      backsubmissionLoader = 'NOT RUNNING'
      floodBot = 'NOT RUNNING'
      logloader = 'NOT RUNNING'

      for pid in pids:
         try:
            with open(os.path.join('/proc', pid, 'cmdline'), 'r') as f:
               cmd = f.read()
               f.close()
            
            if 'logloader.py' in cmd:
               logloader = 'Running'
               
            if 'submissionloader.py' in cmd:
               submissionLoader = 'Running'
            
            if 'datebot.py' in cmd:
               datebot = 'Running'
               
            if 'backsumbissionloader.py' in cmd:
               backsubmissionLoader = 'Running'
               
            if 'submissionbot.py' in cmd:
               floodBot = 'Running'
               
         except IOError: # proc has already terminated
            continue
            
               
      text += '```'   
      text += 'Modlogbot              :       ' + modlogbot + '\n'
      text += 'Datebot                :         ' + datebot + '\n'
      text += 'floodBot               :         ' + floodBot + '\n'
      text += 'load loader            :         ' + logloader + '\n'
      text += 'Submission Loader      :       ' + submissionLoader + '\n'
      text += 'Back Submission Loader :       ' + backsubmissionLoader + '\n'
      
      text += '```'
   
      data['text'] = text

      return data
   # get_userstats()

   def get_modlog(self,interval):
      # did they specify an interval?
      regex = re.search('([\d]+)([HhDdWwMmQq])',interval)

      if regex is not None:
         val = int(regex.group(1))
         interval = regex.group(2)

         if interval == "H" or interval == "h":
            interval ="HOUR"
            if val > 8760:
                val = 8760
         elif interval == "D" or interval == "d":
            interval ="DAY"
            if val > 365:
               val = 365
         elif interval == "W" or interval == "w":
            interval ="WEEK"
            if val > 52:
               val = 52
         elif interval == "M" or interval == "m":
            interval ="MONTH"
            if val > 12:
               val = 12
         elif interval == "Q" or interval == "q":
            interval ="QUARTER"
            if val > 4:
               val = 4
         else:
            val = 24
            interval = "HOUR"
      else:
         val = 24
         internal = "HOUR"
      # if regex is not none

      try:
         db = mysql.connector.connect(user=self.config['database']['user'],
                              password=self.config['database']['password'],
                              database=self.config['database']['dbname'])

         cursor = db.cursor()


         query = ("SELECT moderator, count(*) AS cnt FROM `modlog` WHERE created >= DATE_SUB(NOW(), INTERVAL %s " + interval + ") GROUP BY moderator ORDER BY cnt DESC;")

         cursor.execute(query,(val, ))
         rs = cursor.fetchall()

         # build the message record
         data = {}
         data['token'] = self.config['slack']['webhook_token']
         data['channel'] = self.config['slack']['channel']
         data['attachments'] = []
         text = '*Modlog for the past ' + str(val) + ' ' + interval.lower() + '(s)*'


         if cursor.rowcount == 0:
            attachment = {}
            attachment['fallback'] = '*Modlog for the past ' + str(val) + ' ' + interval.lower() + '(s)*'
            attachment['color'] = 'good'
            attachment['text'] = 'There are no actions in the modlog for this item.'
            data['attachments'].append(attachment)
         else:
            text += '```'
            for item in rs:
               moderator = item[0]
               cnt = str(item[1])

               # ping not, for it is annoying
               safename = moderator[:-1] + "." + moderator[-1] 

               if len(safename) < 21:
                  safename = safename + ' '* (21-len(safename))

               if len(cnt) < 18:
                  cnt = cnt + ' '*(18-len(cnt))

               text += safename + ': ' + cnt + '\n'
            # for
            text += '```'

            data['text'] = text
         # if

         cursor.close()
         db.close()
      except Exception as e:
          data = {}
          data['token'] = self.config['slack']['webhook_token']
          data['channel'] = self.config['slack']['channel']
          data['attachments'] = []
          data['text'] = "That didn't work.  try ~help"


      return data
   # get_modlog()

   def get_userlog(self,user,all=False):
      result = ""
      db = mysql.connector.connect(user=self.config['database']['user'],
                                 password=self.config['database']['password'],
                                 database=self.config['database']['dbname'])

      cursor = db.cursor()

      if all ==True:
         query = ("SELECT action, COUNT(*) AS cnt FROM modlog "
                  "WHERE target_author = %s AND created >= DATE_SUB(NOW(),INTERVAL 6 MONTH) AND action != 'distinguished' AND action != 'editflair' AND action != 'distinguish' GROUP BY action ORDER BY cnt DESC;")
      else:
         query = ("SELECT action, COUNT(*) AS cnt FROM modlog "
                  "WHERE target_author = %s AND created >= DATE_SUB(NOW(),INTERVAL 6 MONTH) AND action != 'distinguished' AND action != 'approvelink' AND action != 'approvecomment' AND action != 'editflair' AND action != 'distinguish' GROUP BY action ORDER BY cnt DESC;")

      cursor.execute(query,(user, ))

      rs = cursor.fetchall()

      actionlist = '```\n'
      for item in rs:
         action = item[0]
         cnt = item[1]

         if len(action) < 20:
            action = action + ' '*(20-len(action))

         actionlist += action + ' : ' + str(cnt) + '\n'
      # for

      actionlist += '```'

      if actionlist == '```\n```':
         actionlist = ''

      cursor = db.cursor()

      if all == True:
         query = ("SELECT action, moderator, target_permalink,created FROM modlog "
                  "WHERE target_author = (%s) AND action != 'distinguished' AND action != 'editflair' AND action != 'distinguish' ORDER BY created DESC LIMIT 10;")
      else:
         query = ("SELECT action, moderator, target_permalink,created FROM modlog "
                  "WHERE target_author = (%s) AND action != 'distinguished' AND action != 'approvelink' AND action != 'approvecomment' AND action != 'editflair' AND action != 'distinguish' ORDER BY created DESC LIMIT 10;")

      cursor.execute(query,(user, ))
      rs = cursor.fetchall()

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']
      data['text'] = '*User report for ' + user + '* (6 Month / last 10)\n' + actionlist
      data['attachments'] = []
      text = '*User log for ' + user + '* (6 Month / last 10)\n'
      
      text += '```'
      if cursor.rowcount == 0:
         attachment = {}
         attachment['fallback'] = 'This user has no actionable items in the modlog.'
         attachment['color'] = 'good'
         attachment['text'] = 'This user has no actionable items in the modlog.'
         data['attachments'].append(attachment)
      else:
         for item in rs:
            action = item[0]
            moderator = item[1]

            # ping not, for it is annoying
            safename = moderator[:-1] + "." + moderator[-1] 

            # a futile attempt at making columns.  fix later
            if len(action) < 20:
               action = action + ' '*(20-len(action))
            
            if len(safename) < 21:
               safename =  safename + ' '*(21-len(safename))

            link = ''
            if len(item[2]) > 0:
               link = self.config['reddit']['root'] + item[2]

            created = item[3].strftime ("%Y-%m-%d %H:%M")
            
            text += action + ' : ' + safename + ' : ' + created +'\n'

            if "approve" in action:
               color = 'good'
            elif "remove" in action:
               color = 'danger'
            elif "edit" in action:
               color = 'warning'
            else:
               color = '#439FE0'
            # if

            '''
            attachment = {}
            attachment['fallback'] = 'user has actions'
            attachment['color'] = color
            attachment['text'] = ''
            attachment['title'] = action
            attachment['title_link'] = link
            attachment['fields'] = []

            field = {}
            field['title'] = ''
            field['value'] = safename + ' : ' + created
            field['short'] = True
            attachment['fields'].append(field)

            data['attachments'].append(attachment)
            '''
         # for
         text += "```"
         data['text'] = text
      # end if
      cursor.close()
      db.close()
      return data
   # get_userlog()

   def get_userstats(self,user,all=False):
      result = ""
      db = mysql.connector.connect(user=self.config['database']['user'],
                                    password=self.config['database']['password'],
                                    database=self.config['database']['dbname'])

      cursor = db.cursor()

      query = ("SELECT action, COUNT(*) as 'c' FROM modlog WHERE target_author = %s AND created >= DATE_SUB(created,INTERVAL 6 MONTH) GROUP BY action ORDER BY c DESC;")


      cursor.execute(query,(user, ))
      rs = cursor.fetchall()

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']
      data['attachments'] = []
      
      text = '*User stats for ' + user + '* (6 Months)\n'

      if cursor.rowcount == 0:
         attachment = {}
         attachment['fallback'] = 'This user has no items in the modlog.'
         attachment['color'] = 'good'
         attachment['text'] = 'This user has no items in the modlog.'
         data['attachments'].append(attachment)
      else:
         text += '```'
         for item in rs:
            action = item[0]
            cnt = item[1]

            # a futile attempt at making columns.  fix later
            if len(action) < 20:
                action = action + ' '*(20-len(action))

            text += action + ' : ' + str(cnt) + '\n'
         # for
         text += '```'
         data['text'] = text
       # end if
      cursor.close()
      db.close()
      return data
   # get_userstats()


   def get_actions(self,permalink):
      result = ""
      reallink = permalink
      if permalink[:6] == "<https":
         shortlink = permalink.replace('https://www.reddit.com','')
         permalink = permalink.replace('https','http',1)
      else:
         shortlink = permalink.replace('http://www.reddit.com','')

      shortlink = shortlink.replace('<','')
      shortlink = shortlink.replace('>','')
      db = mysql.connector.connect(user=self.config['database']['user'],
                              password=self.config['database']['password'],
                              database=self.config['database']['dbname'])

      cursor = db.cursor()

      query = ("SELECT action, moderator, created FROM `modlog` WHERE target_permalink = %s ORDER BY created DESC;")

      cursor.execute(query,(shortlink, ))
      rs = cursor.fetchall()

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']
      data['attachments'] = []
      text = '' + reallink + '\n'

      if cursor.rowcount == 0:
         attachment = {}
         attachment['fallback'] = 'there are no actions in the modlog for this item'
         attachment['color'] = 'good'
         attachment['text'] = 'There are no actions in the modlog for this item.'
         data['attachments'].append(attachment)
      else:
         text += '```'
         for item in rs:
            action = item[0]
            moderator = item[1]
            created = item[2].strftime ("%Y-%m-%d %H:%M:%S")

            # a futile attempt at making columns.  fix later
            if len(action) < 18:
               action = action + ' '* (18-len(action))

            if len(moderator) < 18:
               moderator = moderator + ' '*(18-len(moderator))

            text += action + ':' + moderator + ': ' + created + '\n'

         # for
         text += '```'

         data['text'] = text
      # end if
      cursor.close()
      db.close()
      return data
   # get_actions()

   def get_top(self):
      result = ""
      db = mysql.connector.connect(user=self.config['database']['user'],
                                 password=self.config['database']['password'],
                                 database=self.config['database']['dbname'])

      cursor = db.cursor()

      query = ("SELECT target_author, COUNT(*) AS cnt, action FROM modlog WHERE created >= DATE_SUB(created,INTERVAL 6 MONTH) AND "
               "action != '' AND target_author != '' and action != 'distinguished' AND action != 'approvelink' AND action != 'approvecomment' "
               "AND action != 'editflair' AND action != 'distinguish'  GROUP BY target_author,action   HAVING cnt > 50 ORDER BY `cnt`  DESC;")


      cursor.execute(query)
      rs = cursor.fetchall()

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']

      text = '*Removal counts over 100* (6 Months)\n'

      if cursor.rowcount == 0:
         attachment = {}
         attachment['fallback'] = 'This user has no items in the modlog.'
         attachment['color'] = 'good'
         attachment['text'] = 'This user has no items in the modlog.'
         data['attachments'].append(attachment)
      else:
         text += '```'
         for item in rs:
            target_author = item[0]
            cnt = item[1]
            # a futile attempt at making columns.  fix later
            if len(target_author) < 35:
                target_author = target_author + ' '*(35-len(target_author))

            text += target_author + ' : ' + str(cnt) + '\n'
         # for
         text += '```'
         data['text'] = text
      # end if
      cursor.close()
      db.close()
      return data
   # get_top()

   def get_help(self):

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']

      text = '*modlogbot help*\n```'

      text += '~xactions link        : shows moderator xactions for a given item\n\n'
      text += '~xmodlog interval     : show modlog for a specified interval.  Number + \n\n'
      text += '                        h = Hours, d = Days, w = Weeks, m = Months \n\n'
      text += '                        q = Quarter\n\n'
      text += '                         example: ~xmodlog 24h    or ~xmodlog 2w   \n\n'
      text += ''
      text += '~userlog username    : show mod log history for this user\n\n'
      text += '~userstats username  : show number of actions in the past 6 months\n\n'
      text += '                       includes all actions\n\n'
      text += '~top                 : show people with over 50 actions in 6 months\n\n'

      text += '```'

      data['text'] = text
      return data
   # get_help()

   def get_domain(self,domain):
      result = ""
      bad_domain = False
      if '|' in domain:
         domain = domain.replace('<','').replace('>','').split('|')[1]
      else:
         bad_domain = True

      db = mysql.connector.connect(user=self.config['database']['user'],
                                    password=self.config['database']['password'],
                                    database=self.config['database']['dbname'])

      cursor = db.cursor()

      # because procs don't work they way i expected them to in python
      query = (
         "SELECT DISTINCT(action), COUNT(*) AS cnt, "
         "("
         "   SELECT created FROM modlog_submissions WHERE domain = %s AND `action` IN('removelink','approvelink') "
         "   ORDER BY created ASC limit 1 "
         ") AS 'Oldest', "
         "("
         "   SELECT created FROM modlog_submissions WHERE domain = %s AND `action` IN('removelink','approvelink') "
         "   ORDER BY created DESC limit 1 "
         ") AS 'Newest' "
         "FROM modlog_submissions WHERE domain = %s AND action IN ('removelink', 'approvelink') "
         "GROUP BY domain, action ORDER BY domain, cnt DESC;"
      )

      args = ( domain,domain,domain )
      cursor.execute(query,args)

      # build the message record
      data = {}
      data['token'] = self.config['slack']['webhook_token']
      data['channel'] = self.config['slack']['channel']
      rs = cursor.fetchall()
      if cursor.rowcount == 0 or bad_domain:
         cursor.close()
         db.close()
         data['attachments'] = []
         attachment = {}
         attachment['fallback'] = 'There are no submissions from this domain.'
         attachment['color'] = 'good'
         attachment['text'] = 'There are no submissions from this domain'
         data['attachments'].append(attachment)
         data['text'] = "There are no submissions from this domain"
         return data
      else:
         text = '```'

         for item in rs:
            print(item)
            action = item[0]
            cnt = item[1]
            oldest = item[2].strftime ("%Y-%m-%d %H:%M:%S")
            newest = item[3].strftime ("%Y-%m-%d %H:%M:%S")

            # a futile attempt at making columns.  fix later
            if len(action) < 20:
               action = action + ' '*(20-len(action))

               text += action + ' : ' + str(cnt) + '\n'

         # for
         text += '```'

         heading = 'Domain:  *' + domain + '*\n'
         heading += 'Oldest: *' + oldest + '*\n'
         heading += 'Newest: *' + newest + '*\n\n'
         data['text'] = heading + text
      # end if
      cursor.close()
      db.close()
      return data
   # get_domain()

   def run(self):
      while True:
         data = self.slack.rtm_read()

         if not data:
            continue
         elif 'type' not in data[0]:
            continue
         elif data[0]['type'] != 'message':
            continue
         elif 'text' not in data[0]:
            continue
         elif data[0]['text'] == '':
            continue
         elif data[0]['text'][0] != '~' and data[0]['channel'] != self.config['slack']['channel_userlog']:
            continue

         chan = data[0]['channel']
         args = str(data[0]['text']).split(' ')
         doAll = False
         if len(args) >= 2:
            username = args[1]
            print('Command: ' + args[0])
            print('Args[1]  ' + args[1])

         if '~userlog' in args[0] or '~userstats' in args[0]:
            message = self.get_userstats(username,doAll)
            stats = message['text']
            log = self.get_userlog(username,doAll)['text']
            
            message['text'] += '\n\n' + log
         elif '~top' in args[0]:
            message = self.get_top()
         elif '~xactions' in args[0]:
            link = args[1]
            message = self.get_actions(link)
         elif '~xmodlog' in args[0]:
            interval = args[1]
            message = self.get_modlog(interval)
         elif '~domain' in args[0]:
            domain = ''
            try:
               domain = args[1]
            except:
                pass
            message = self.get_domain(domain)
         elif '~bots' in args[0]:
            message = self.get_bots()
         elif '~help' in args[0]:
            message = self.get_help()
         else:
            message = '';
            
            
         # special userlog channel stuff 
         if chan == self.config['slack']['channel_userlog']:
            username = data[0]['text']
            
            # are we a url maybe?
            if "/" in username:
               try:
                  parts = username.split('/')
                  username = parts[-1].replace('>','')
               except:
                  pass
                  
            # put them together and what have you got?
            try:
               message = self.get_userstats(username,doAll)
               stats = message['text']
               log = self.get_userlog(username,doAll)['text']
               message['text'] += '\n\n' + log
            except:
               message = ''

         if message != '':
            try:
               if 'attachments' in message:
                  self.slack.api_call('chat.postMessage', as_user=True,
                                      channel=chan, text=message['text'],attachments=json.dumps(message['attachments']))
               else:
                  self.slack.api_call('chat.postMessage', as_user=True,
                                   channel=chan, text=message['text'])
            except:
               print("There was a problem sending the slack message")
               time.sleep(5)
               pass

   # run()


class handler(BaseHTTPRequestHandler):
   def __config__(self):
      with open('config.json','r') as f:
         self.config = json.load(f);

   def do_POST(self):
      self.__config__()
      ctype, pdict = cgi.parse_header(self.headers['content-type'])
      if ctype == 'multipart/form-data':
         postvars = cgi.parse_multipart(self.rfile, pdict)
      elif ctype == 'application/x-www-form-urlencoded':
         length = int(self.headers['content-length'])
         postvars = urllib.parse.parse_qs(self.rfile.read(length).decode("utf8"))
      else:
         postvars = {}


      args = str(postvars['text'][0]).split(' ')
      doAll = False
      if len(args) >= 2:
         username = args[1]
         print('Fetching ' + username)

      if str(postvars['token'][0]) in self.config['slack']['webhook_token']:
         self.send_response(200)
         self.send_header('Content-type','application/json')

         self.end_headers()

         modlogbot = bot()

         if '~userlog' in args[0]:
             message = modlogbot.get_userlog(username,doAll)
         elif '~userstats' in args[0]:
             message = modlogbot.get_userstats(username,doAll)
         elif '~top' in args[0]:
             message = modlogbot.get_top()
         elif '~xactions' in args[0]:
             link = args[1]
             message = modlogbot.get_actions(link)
         elif '~xmodlog' in args[0]:
             interval = args[1]
             message = modlogbot.get_modlog(interval)
         elif '~domain' in args[0]:
             domain = args[1]
             message = modlogbot.get_domain(domain)
         else:
             message = modlogbot.get_help()


         self.wfile.write(bytes(json.dumps(message),"utf8"))
         return
      else:
         print('Invalid token')
         self.send_response(403)
         return



print("starting")

print("reading config")
with open('config.json','r') as f:
   config = json.load(f);

if config['slack']['mode'] == "bot":
   # do bot things
   bot = bot()

   bot.slack_connect()
   bot.run()
elif config['slack']['mode'] == "webhook":
   # do webhook things
   print("Starting HTTP server")
   httpd = HTTPServer(('0.0.0.0',8777),handler)
   print("running")
   httpd.serve_forever()
else:
   print("invalid slack mode")

print("exiting")
