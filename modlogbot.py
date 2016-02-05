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
from pprint import pprint
import inspect
from database import database
from http.server import BaseHTTPRequestHandler, HTTPServer


class bot(object):
    def __init__(self):
        self.__config__()
        self.enabled=True

    def __config__(self):
        with open('config.json','r') as f:
            self.config = json.load(f);

    def get_userlog(self,user,all=False):
       result = ""
       db = mysql.connector.connect(user=self.config['database']['user'],
                                    password=self.config['database']['password'],
                                    database=self.config['database']['dbname'])

       cursor = db.cursor()

       if all ==True:
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
       data['text'] = '*User report for ' + user + '*'
       data['attachments'] = []

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
               safename =  u'{}\u200B{}'.format(moderator[0], moderator[1:])

               # a futile attempt at making columns.  fix later
               if len(action) < 20:
                   action = action + ' '*(20-len(action))

               if len(safename) < 20:
                   safename =  safename + ' '*(20-len(safename))

               link = ''
               if len(item[2]) > 0:
                   link = self.config['reddit']['root'] + item[2]

               created = item[3].strftime ("%Y-%m-%d %H:%M")

               if "approve" in action:
                   color = 'good'
               elif "remove" in action:
                   color = 'danger'
               elif "edit" in action:
                   color = 'warning'
               else:
                   color = '#439FE0'

               attachment = {}
               attachment['fallback'] = 'user has actions'
               attachment['color'] = color
               attachment['text'] = ''
               attachment['title'] = action
               attachment['title_link'] = link
               # construct the raw message
              # print(json.dumps(attachment))
               data['attachments'].append(attachment)
               attachment['fields'] = []

               field = {}
               field['title'] = 'Moderator'
               field['value'] = safename
               field['short'] = True
               attachment['fields'].append(field)

               field2 = {}
               field2['title'] = 'Date'
               field2['value'] = created

               attachment['fields'].append(field2)
          # for
       # end if
       cursor.close()
       db.close()
       return data

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

       text = '*User stats for ' + user + '* (6 Months)'

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

    def get_help(self):

        # build the message record
        data = {}
        data['token'] = self.config['slack']['webhook_token']
        data['channel'] = self.config['slack']['channel']

        text = '*modlogbot help*\n```'

        text += '~userlog username    : show mod log history for this user\n\n'
        text += '~userstats username  : show number of actions in the past 6 months\n\n'
        text += '                       includes all actions\n\n'
        text += '~top                 : show people with over 50 actions in 6 months\n\n'
        text += '```'

        data['text'] = text
        return data

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

        if str(postvars['token'][0]) == self.config['slack']['webhook_token']:
            self.send_response(200)
            self.send_header('Content-type','application/json')

            self.end_headers()

            modlogbot = bot()

            if 'userlog' in args[0]:
                message = modlogbot.get_userlog(username,doAll)
            elif 'userstats' in args[0]:
                message = modlogbot.get_userstats(username,doAll)
            elif 'top' in args[0]:
                message = modlogbot.get_top()
            else:
                message = modlogbot.get_help()

                
            self.wfile.write(bytes(json.dumps(message),"utf8"))
            return
        else:
            print('Invalid token')
            self.send_response(403)
            return



print("Starting server")
httpd = HTTPServer(('0.0.0.0',8777),handler)
print("running")
httpd.serve_forever()
