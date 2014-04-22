##this script collects data from Facebook I had to build it without importing
##a facebook module because it has not been approved for use in the office
# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import time
import regex
import re
import csv


class FPA:

    def __init__(self,token):
        """
        This function initializes the class FPA
        ex.
        datacull = FPA("token")
        """
        
        #initializes the class and sets up the tokens
        self.token = token

        #set up the current time
        self.date = time.time()
        self.firstday = str(int(time.time()))
        self.lastday = str(int(self.date - 31536000))

        self.limit = '500'


    def initmainfile(self,mainfile = "postings.txt"):
        """
        This function initializes the main export file
        """        
        
        self.main_export_file  = mainfile
        with open(self.main_export_file,'wb') as csvfile:
                    contentwriter = csv.writer(csvfile)
                    contentwriter.writerow([
                    'post_id', 'pagename', 'pageid', 'message', 'kind',
                    'created_time', 'shares', 'likes', 'comments', 'link'
                                           ])        
        


    def initengagmentbank(self,mainfile = "engagement_bank.txt" ):
        """
        This function initializes the main engagement export file
        """    
        self.engagement_bank  = mainfile
        with open(self.engagement_bank,'wb') as csvfile:
                    contentwriter = csv.writer(csvfile)
                    contentwriter.writerow(["postid","userid","type",
                    "time","message"])
        
    def getposts(self,pages):
        """
        This function get the posts
        """    

        if type(pages) == str:
            pages = [pages]
        else:
            pass
        with open(self.main_export_file,'ab') as csvfile:
                
            for page in pages:
                #define the page and parameters
                url = "https://graph.facebook.com/" + regex.sub("\r|\n| ","",page) + "/posts?"
                headers =  urllib.urlencode({
                                'limit':self.limit,
                                'until':self.firstday,
                                'date_format':'U',
                                'fields':'message,shares,link,id,from,type,likes.summary(true).limit(1),comments.summary(true).limit(1)',
                                'access_token':self.token
                                })
                #try link
                try:
                    #get the url
                    response = urllib2.urlopen(url + headers)
                except:
                    print "This link didn't work, Are you sure you put in the page correctly?"
                    continue
        
                main_dic = json.load(response)
        
                #get page name: try to see if fail
                try:
                    pageid = str(main_dic['data'][0]['from']['id'].encode('utf-8'))
                    pagename = str(main_dic['data'][0]['from']['name'].encode('utf-8'))
                except:
                    print "This is no page! Are you sure you put in the page correctly?"
                    continue
        
                #start a loop for paging
                i = True
                counter = 1
                print "Working on: " + page + " Page # ",
                while i == True:
                    print str(counter),
                    counter += 1
                        
                    #extract posts
                    for post in main_dic['data']:
        
                        created_time = post['created_time']
                        if int(self.lastday) > created_time:
                            print " Done!"
                            i = False
                            break
                        created_time = str(created_time)
                        
                        #get the type of post, time, and post id
                        kind = post['type'].encode('utf-8')
                        post_id = post['id'].encode('utf-8')
                        
                        #get the message
                        if "message" in post.keys():
                            message = post['message'].encode('utf-8')
                            #message = regex.sub('\t|\n|\r|\"',"",message)                
                        else:
                            message = "No Message"
        
                        #get link
                        if "link" in post.keys():
                            link = post['link'].encode('utf-8')
                        else:
                            link = ""
        
                        #get the number of shares
                        if "shares" in post.keys():
                            shares = str(post['shares']['count'])
                        else:
                            shares = "0"
        
                        #get the likes
                        if "likes" in post.keys():
                            likes = str(post['likes']['summary']['total_count'])
                        else:
                            likes = "0"
        
                        #get the comments
                        if "comments" in post.keys():
                             comments = str(post['comments']['summary']['total_count'])
                        else:
                            comments = "0"
        
                        #print post info
                        
                        contentwriter = csv.writer(csvfile)
                        contentwriter.writerow([
                            post_id, pagename, pageid, message, kind,
                            created_time, shares, likes, comments, link
                                                ])
            
                    #determin to continue
                    nextpage =  main_dic['paging']['next'].encode('utf-8')
                    response = urllib2.urlopen(nextpage)
                    main_dic = json.load(response)
                    if 'data' not in main_dic.keys():
                        print "No data for page: " + page
                        break

    def getlikes(self, post_ids):
        
        """
        This function get the likes
        """    

        with open(self.engagement_bank,'ab') as csvfile:
            contentwriter = csv.writer(csvfile)
                    

            for post_id in post_ids:
            
                #define the headers
                headers =  urllib.urlencode({
                                'limit':'100000000',
                                'fields':'username,id',
                                'access_token':self.token
                                })
                #and the url
                response = urllib2.urlopen("https://graph.facebook.com/" +
                                            post_id + "/likes?"+ headers)
                #begin loop
                is_next = True
    
                while is_next:
                    likes_dic = json.load(response)
    
                    #check to see if there are any likes
                    if "data" not in likes_dic.keys():
                        break 
    
                    #loop through the data and get
                    for liker in likes_dic['data']:
                        contentwriter.writerow([
                        post_id, "#" + liker['id'].encode('utf-8'), "like"
                                                ])
    
                    #get the totals on the first run and check to see if there is a next
                    if "next" not in likes_dic.keys():
                        is_next = False
                    else:
                        response = urllib2.urlopen(likes_dic['next'])



    def getcomments(self, post_ids):

        """
        This function get the comments
        """   

        with open(self.engagement_bank,'ab') as csvfile:
            contentwriter = csv.writer(csvfile)
                    
            for post_id in post_ids:
                #define the headers
                headers =  urllib.urlencode({
                                'fields':'comments.limit(100000).fields(from,message,created_time)',
                                'date_format':'U',
                                'access_token':self.token
                                })
                #and the url
                response = urllib2.urlopen("https://graph.facebook.com/" + post_id + "?" + headers)
                #begin loop
                is_next = True
    
                while is_next:
                    comment_dic = json.load(response)
    
                    #check to see if there are any comments
                    if "comments" not in comment_dic.keys():
                        break
                    elif "next" in comment_dic['comments']['paging'].keys():
                        response = urllib2.urlopen(comment_dic['comments']['paging']['next'].encode('utf-8'))
                    else:
                        is_next = False
                    
                    #loop through the data and get
                    for commenter in comment_dic['comments']['data']:
                        try:
                            message = commenter['message'].encode('utf-8')
                            #message = re.sub('\t|\n|\r|',"",message)
                            contentwriter.writerow([
                                    post_id, "#" + str(commenter['from']['id']),
                                     "comment" , str(commenter['created_time']), 
                                     message])
                                
                        except:
                            print message
                        

        
                
if __name__ == '__main__':
    
    instance = FPA("") 
    instance.initmainfile(r"C:\Users\gramirez\Desktop\#yali\test1.csv")     
    instance.getposts(['bla'])
    instance.initengagmentbank()
    instance.getcomments()
    instance.getlikes()
