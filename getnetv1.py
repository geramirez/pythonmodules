#!/usr/bin/python
# -*- coding: utf-8 -*-

import oauth2 as oauth
import urllib2 as urllib
import json
import datetime
from random import seed, randrange, shuffle
from math import sqrt
import sys
import regex
import csv

class twitterapi:
    def __init__(self,anon):
        self.anon = anon
        self.cipher = self.cipher()
        self.exempt = []
        self.key = 1
        self.sinceid = "-1"
        
    def getkeys(self,keyfile = "consumer_keys.csv"):
                #set a key holder
                self.keys = {}
                #set key counter
                i = 1
                #open csv file and read off keys
                with open(keyfile,'rb') as csvfile:
                        keyfile = csv.reader(csvfile,delimiter=',')
                        for row in keyfile:
                                self.keys[i] = row
     
    def twitterreq(self,originalurl):
        
                
                consumer_key = self.keys[self.key][0]
                consumer_secret = self.keys[self.key][1]
                access_token_key = self.keys[self.key][2]
                access_token_secret = self.keys[self.key][3]

                _debug = 0

                oauth_token= oauth.Token(key=access_token_key, secret=access_token_secret)
                oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
                signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

                http_method = "GET"

                http_handler= urllib.HTTPHandler(debuglevel=_debug)
                https_handler = urllib.HTTPSHandler(debuglevel=_debug)


                req = oauth.Request.from_consumer_and_token(oauth_consumer,
                token=oauth_token,
                http_method=http_method,
                http_url=originalurl, 
                parameters=self.parameters)

                req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

                headers = req.to_header()

                if http_method == "POST":
                        encoded_post_data = req.to_postdata()
                else:
                        encoded_post_data = None
                        url = req.to_url()

                        opener = urllib.OpenerDirector()
                        opener.add_handler(http_handler)
                        opener.add_handler(https_handler)

                response = opener.open(url, encoded_post_data)
                response = json.load(response) 
                         
                if 'errors' in response.keys():
                        print(response)
                        if response['errors'][0]['code'] == 88:
                                print( "moving to key: " + str(self.key))
                                self.key += 1
                                return self.twitterreq(originalurl)
                        else:
                                print(response)
                                exit()
                else:
                        return response

    def cipher(self):
                now = datetime.datetime.now()
                seed(now.day + now.year + now.month)

                alpha13 = ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'a', 's', 'd',
                           'f', 'g', 'h', 'j', 'k', 'l', 'q', 'w', 'e', 'r',
                           't', 'y', 'u', 'i', 'o', 'p', '0', '9', '8', '7', 
                           '6', '5', '4', '3', '2', '1']
                
                shuffle(alpha13)
                alpha13 = "".join(alpha13)
                
                extra5 = randrange(10000,99999)
                
                return [alpha13,extra5]
    
    def encoder(self,user):
                """ str -> str
                >>> encoder("user")
                sfjisjdfl323 (something like that)
                
                """
                #break the codes into 2 comps
                cipher = self.cipher[0]
                extra5 = self.cipher[1]

                user = regex.sub("\W","",user.lower())
                alpha   = 'abcdefghijklmnopqrstuvwxyz1234506789'
                encoded13 = 1
                
                i = 1.0
                
                for c in user:
                    if c in alpha:
                        # use the index
                        c = cipher[alpha.index(c)]
                        
                    encoded13 = encoded13 * ord(c) * i/139.0      
                    i += 1.0
                    
                encoded = str(sqrt(encoded13*extra5*1000000))
                encoded = encoded.replace("e+","")
                return "@" + encoded.replace(".","")

    def snaprint(self, tweet_dic):
               
               with open(self.filename,'ab') as csvfile:
                        elements = csv.writer(csvfile, delimiter = ',')
                        elements.writerow(['tweet',''] + tweet_dic.values())
                        
                        if tweet_dic['user_mentions'] != []:
                                for connection in tweet_dic['user_mentions']:
                                        elements.writerow(['user',connection] \
                                        + tweet_dic.values())
                        
                        if tweet_dic['hashtags'] != []:
                                for connection in tweet_dic['hashtags']:
                                        elements.writerow(['hashtags',connection] \
                                            + tweet_dic.values())

                        if tweet_dic['urls'] != []:
                                for connection in tweet_dic['urls']:
                                        elements.writerow(['urls',connection] \
                                        + tweet_dic.values())


    def snaprint_anon(self, tweet_dic):
        
                with open(self.filename,'ab') as csvfile:
                        elements = csv.writer(csvfile, delimiter = ',')
                        elements.writerow(['tweet',''] + tweet_dic.values())
                        
                        if tweet_dic['user_mentions'] != []:
                                for connection in tweet_dic['user_mentions']:
                                        elements.writerow(['user',connection] \
                                        + tweet_dic.values())
                        
                        if tweet_dic['hashtags'] != []:
                                for connection in tweet_dic['hashtags']:
                                        elements.writerow(['hashtags',connection] \
                                        + tweet_dic.values())

                        if tweet_dic['urls'] != []:
                                for connection in tweet_dic['urls']:
                                        elements.writerow(['urls',connection] \
                                        + tweet_dic.values())
                

    def DBmaker(self,main_dic):

                #makes an empty tweet dictionary to hold info
                tweet_dic = {}
                #itterates over each tweet
                for tweet in main_dic[u'statuses']:
                        #created at tag
                        tweet_dic['created_at'] = tweet[u'created_at'].encode('utf-8')

                        #extracts from_user
                        tweet_dic['from_user'] = "@" + tweet['user']['screen_name'].encode('utf-8')
        
                        #extracts tweet id
                        tweet_dic['id'] = tweet[u'id_str'].encode('utf-8')

                        #extract source
                        tweet_dic['source'] = tweet[u'source'].encode('utf-8')

                        #extract withheld
                        if tweet.has_key('withheld_in_countries'):
                                tweet_dic['withheld_in_countries'] = tweet['withheld_in_countries']
                        else:
                                tweet_dic['withheld_in_countries'] = ""

                        #get the max id that will be put back into the api call
                        self.max_id = tweet['id'] - 1

                        #extract follower count and other user info 
                        tweet_dic['followers'] = str(tweet['user']['followers_count'])
                        tweet_dic['user_created_at'] = str(tweet['user']['created_at'])
                        tweet_dic['user_lang'] = str(tweet['user']['lang'])
                        tweet_dic['user_statuses'] = str(tweet['user']['statuses_count'])
                        tweet_dic['user_utc_offset'] = str(tweet['user']['utc_offset'])

                        #extract urls
                        tweet_dic['urls'] = ""
                        if tweet['entities'].has_key('urls'):
                                tweet_dic['urls'] = []
                                for url in tweet[u'entities'][u'urls']:
                                        tweet_dic['urls'] = tweet_dic['urls'] + [url[u'expanded_url'].encode('utf-8')]

                        #extracts hashtags
                        tweet_dic['hashtags'] = ''
                        if tweet['entities'].has_key('hashtags'):
                                tweet_dic['hashtags'] = []
                                for tag in tweet[u'entities'][u'hashtags']:
                                        tweet_dic['hashtags'] = tweet_dic['hashtags'] + [tag[u'text'].encode('utf-8')]
 
                        #extract time zone
                        tweet_dic['time_zone'] = ""
                        if tweet['user']['time_zone'] != None:
                                tweet_dic['time_zone'] = tweet['user']['time_zone'].encode('utf-8')

                        #extract retweets 
                        tweet_dic['retweet_count'] = str(tweet['retweet_count'])

                        #extract favorites 
                        tweet_dic['favorite_count'] = "" 
                        if tweet['metadata'].has_key('favorite_count'):
                                tweet_dic['favorite_count'] = str(tweet['metadata']['favorite_count'])

                        #extracts text into string
                        tweet_text = tweet[u'text'].encode('utf-8')
                        tweet_dic['text'] = regex.sub('\t|\n|\r|,|"',"",tweet_text)

                        #extracts user_mentions
                        tweet_dic['user_mentions'] = ''
                        if tweet[u'entities'][u'user_mentions'] != []:
                                tweet_dic['user_mentions'] = []
                                for user in tweet[u'entities'][u'user_mentions']:
                                        tweet_dic['user_mentions'] = tweet_dic['user_mentions'] + ["@" + user[u'screen_name'].encode('utf-8')]
 
                        #extracts media type
                        tweet_dic['media_type'] = ''
                        tweet_dic['media_url'] = ''
                        if tweet['entities'].has_key('media'):
                                tweet_dic['media_type'] = []
                                tweet_dic['media_url'] = []
                                for media in tweet['entities'][u'media']:
                                        tweet_dic['media_type'] = tweet_dic['media_type'] + [media[u'type'].encode('utf-8')]
                                        tweet_dic['media_url'] = tweet_dic['media_url'] + [media[u'media_url'].encode('utf-8')]


                        #extract reply
                        tweet_dic['in_reply_to_screen_name'] = str(tweet['in_reply_to_screen_name'])

                        #extract reply status
                        tweet_dic['in_reply_to_status_id_str'] = str(tweet['in_reply_to_status_id_str'])

                        #extract language
                        tweet_dic['lang'] = tweet['lang']
                        
                        if self.anon == True:
                            
                                tweet_dic['text'] = tweet_dic['text'].replace('"',"'")
                
                                ##anon the from user
                                tweet_dic['from_user'] = self.encoder(tweet_dic['from_user'])
                                tweet_dic['in_reply_to_screen_name'] = self.encoder(tweet_dic['in_reply_to_screen_name'])
                
                                #annon the rest
                                if tweet_dic['user_mentions'] != []:
                                        i = 0
                                        for mention in tweet_dic['user_mentions']:
                                                #anon the mentio
                                                mention_anon = self.encoder(mention)
                                                #replace in text
                                                tweet_dic['text'] = regex.sub(mention,mention_anon,tweet_dic['text'])
                                                #replace in mentions and move to the next one
                                                tweet_dic['user_mentions'][i] = mention_anon
                                                i += 1

                                self.snaprint(tweet_dic)

                        else:
                                self.snaprint(tweet_dic)

    def search(self,searchterm):

                #tell it to keep going
                keepgoing = True

                # set url + parameters
                url = "https://api.twitter.com/1.1/search/tweets.json"
                self.parameters = {'q':searchterm,'count':'500','result_type':'recent',
                                   'include_entities':'true','since_id':str(self.sinceid)} 

                main_dic = self.twitterreq(url)

                while keepgoing == True:

                        if "errors" in main_dic.keys():
                                print(main_dic)
                                break

                        elif main_dic['statuses'] == []:
                                print("There are no more Statuses")
                                break

                        else:
                                self.DBmaker(main_dic)
                                self.parameters['max_id'] = self.max_id
                                main_dic = self.twitterreq(url)
                        
                                
    def initexportfile(self,filename = "export.csv"):
        
                self.filename = filename
                with open(filename,'wb') as csvfile:
                        headerwriter = csv.writer(csvfile, delimiter = ',')
                        headerwriter.writerow(['type','connection','user_lang',
                                    'text', 'hashtags', 'user_utc_offset',
                                    'id', 'favorite_count', 'source',
                                    'in_reply_to_screen_name',
                                    'followers', 'retweet_count',
                                    'media_type', 'media_url',
                                    'user_mentions', 'withheld_in_countries',
                                    'from_user', 'lang', 'user_created_at',
                                    'created_at', 'time_zone', 'user_statuses',
                                    'in_reply_to_status_id_str','url'])
                

    def decoder(self,decoderfile="decoder.csv",propfile="dosholder.txt"):
                f = open(propfile,'r')
                export = open(decoderfile,'w')
                export.write('"' + "user" + '","' + "user_anon"  + '"\n')
                for user in f:
                    user = user.replace("\W","").lower()
                    user_anon = self.encoder(user)
                    export.write('"' + user + '","' + user_anon  + '"\n')
        
                f.close()
                export.close()

if __name__ == '__main__':
        #edit for searching in non english languages
        reload(sys)
        sys.setdefaultencoding("utf-8")
        #if true the output will be anonymized if false it will not
        instance = twitterapi(False)
        #iniciate file
        instance.initexportfile()
        #get keys
        instance.getkeys()
        #set search term        
        instance.search("russia")
