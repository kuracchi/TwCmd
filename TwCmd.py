# -*- coding: utf-8 -*-

import tweepy
from cmd import Cmd
import sys

import banner
import conf
import re

in_encode = sys.stdin.encoding
out_encode = sys.stdout.encoding

try:
    if conf.access_token and conf.access_secret:
        default_auth = True
    else:
        default_auth = False
except:
    default_auth = False

tl_default_num = 30
tweet_tmpl = "\n[%s] : %s >> %s"

digitReg = re.compile(r'^[0-9]+$')
def isdigit(s):
    return digitReg.match(s) is not None

class TwCmd(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        self.intro = banner.twcmd_banner
        self.prompt = "Twitter >>> "
        self.auth = None
        self.api = None
        self.auth = None
        self.key = None
        self.secret = None


    def emptyline(self):
        pass


    def do_tw(self, tweet):
        try:
            if self.api:
                s = self.api.update_status(tweet)
                print (tweet_tmpl 
                       % (s.created_at, s.user.screen_name, s.text))
            else:
                print("Please login using 'login' command first")

        except(Exception, e):
            print("Tweet failed : ", e)
            

    def do_mentions(self, dummy):
        try:
            mentions = self.api.mentions_timeline()
            mentions.reverse()
            for m in mentions:
                print (tweet_tmpl 
                       % (m.created_at, m.user.screen_name,m.text))
        except:
            pass
            

    def do_favorite(self, dummy):
        try:
            mentions = self.api.mentions_timeline()
            mentions.reverse()
            for m in mentions:
                if None == m.in_reply_to_status_id:
                    self.api.create_favorite(m.id)
                    print ("\n[%s] : %s >> [%s]%s" 
                           % (m.created_at, m.user.screen_name,m.in_reply_to_status_id, m.text))
        except:
            pass
                

    def do_tl(self, line):
        try:
            num = tl_default_num
            nameFlg = False
            reverseFlg = False
            name = ""
            for s in line.split():
            	if isdigit(s):
	                try:
	                    num = int(s)
	                except(Exception, e):
	                    print (e)
            	elif 're' == s:
                    reverseFlg = True
            	else:
            		nameFlg = True
            		name = s
            timeline = []
            if nameFlg:
                timeline = self.api.user_timeline(id=name,count=num)
            else:
                timeline = self.api.home_timeline(count=num)
            if False == reverseFlg:
                timeline.reverse()
            for tw in timeline:
                print ("\n[%s] : %s ( %s ) >> %s" 
                       % (tw.created_at, tw.user.screen_name, tw.user.name, tw.text))

        except(Exception, e):
            print (e)

    def help_tl(self):
        print ("usage : tl [# of tweets]")
                

    def do_search(self, line):
        try:
            num = tl_default_num
            query = []
            for s in line.split():
            	if isdigit(s):
	                try:
	                    num = int(s)
	                except(Exception, e):
	                    print (e)
            	else:
            		query.append(s)
            if len(query) == 0:
                return
            timeline = self.api.search(q=query, count=num)
            timeline.reverse()
            for tw in timeline:
                print ("\n[%s] : %s ( %s ) >> %s" 
                       % (tw.created_at, tw.user.screen_name, tw.user.name, tw.text))

        except(Exception, e):
            print (e)

    def help_search(self):
        print ("Returns tweets that match a specified query.")
        print ("usage : search [search query] [# of tweets]")


    def do_user(self, line):
        usernames = line.split()
        if len(usernames) == 0:
            users = [self.api.me()]
        else:
            users = [self.api.get_user(u) for u in usernames]
        for u in users:
            print ("\n[%s] %s (%s) : following %s  follower %s\n\t%s"
                   % (u.id, u.screen_name, u.name, u.friends_count, 
                      u.followers_count, u.description, ))

    def help_user(self):
        print ("Returns information about the specified user.")
        print ("usage : user [id | user_id | screen_name]")


    def do_friends(self, line):
        s = line.split()
        friends_ids = []
        no = 0
        user_id = self.api.me().id
        if len(s) > 0:
            user_id = s[0]
        friends_ids=self.api.friends_ids(id=user_id)
        friends_ids.reverse()
        for i in range(0, len(friends_ids), 100):
           for u in self.api.lookup_users(user_ids=friends_ids[i:i+100]):
               no = no + 1
               print ("No.%s [%s] %s (%s) : following %s  follower %s"
                   % (no, u.screen_name, u.name, u.id, u.friends_count, 
                      u.followers_count,  ))

    def do_profile(self, line):
        self.api.update_profile(description=line)
        u=self.api.me()
        print ("\n[%s] %s (%s) : following %s  follower %s\n\t%s"
                   % (u.id, u.screen_name, u.name, u.friends_count, 
                      u.followers_count, u.description, ))

    def help_profile(self):
        print ("Sets values that users are able to set under the “Account” tab of their settings page.")
        print ("usage : profile [description]")

    def do_login(self, line):
        s = line.split()
        try:
            auth = tweepy.OAuthHandler(conf.consumer_key,
                                       conf.consumer_secret)

            if not default_auth:
                redirect_url = auth.get_authorization_url()
                print ("\nGet PIN code from following URL and input it\n%s\n"
                       % redirect_url)
                verifier = raw_input("input PIN code: ").strip()

                auth.get_access_token(verifier)
                self.key = auth.access_token.key
                self.secret = auth.access_token.secret

            else:
                self.key = conf.access_token
                self.secret = conf.access_secret

            auth.set_access_token(self.key, self.secret)
            self.api = tweepy.API(auth)
            print ("%s logged in" % self.api.me().screen_name)
            self.auth = auth

        except(Exception, e):
            print (e)
            self.help_login()

    def help_login(self):
        print (banner.help_login)


if __name__ == '__main__':

    tw = TwCmd()
    tw.cmdloop()
