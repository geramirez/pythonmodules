##this script collects data from Facebook I had to build it without importing
##a facebook or csv module because they had not been approved for use in the office
##I'm curretnly updating it to work with the csv writer

import urllib2
import urllib
import json
import time
import sys
import regex
import re


class FPA:

    def __init__(self,token):
        """
        This function initializes the class FPA
        ex.
        datacull = FPA("iGoI9ZCHaat9QcqPMUIbxH3DqbNGf3ne5Ko6VHy5ZC8eyUUUHhSlGYliA2B12coewui1hY3AEMTt8NmILnt1BDoIdJKKZAncSxcG4PnPeH1i5QEAFAZD")
        """
        
        #initializes the class and sets up the tokens
        self.token = token

        #set up the current time
        self.date = time.time()
        self.firstday = str(int(time.time()))
        self.lastday = str(int(self.date - 31536000))

        self.limit = '500'


    def initmainfile(self,mainfile = "postings.txt"): 
        self.main_export_file  = mainfile
        f = open(self.main_export_file ,'w')
        f.write("postid" + '\t' + "pagename" + '\t' + "pageid" + '\t' + "message" + '\t' + "kind" + '\t')
        f.write("created_time" + '\t' + "shares" + '\t' + "likes" + '\t' + "comments" + '\t' + "link" + "\n")
        f.close()

    def initengagmentbank(self,mainfile = "engagement_bank.txt" ):
        self.engagement_bank  = mainfile
        f = open(self.engagement_bank ,'w')
        f.write("postid" + '\t' + "userid" + '\t' + "type" + '\t' + "time" + '\t' + "message" + '\n')
        f.close()

    def getposts(self,page):
        #open the file we will be writing into
        f = open(self.main_export_file, "a")

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
            response = urllib2.urlopen("https://graph.facebook.com/" +
                                       regex.sub("\r|\n| ","",page) +
                                       "/posts?" + headers)
        except:
            print "This link didn't work, Are you sure you put in the page correctly?"
            return

        main_dic = json.load(response)

        #get page name: try to see if fail
        try:
            pageid = str(main_dic['data'][0]['from']['id'].encode('utf-8'))
            pagename = str(main_dic['data'][0]['from']['name'].encode('utf-8'))
        except:
            print "This is no page! Are you sure you put in the page correctly?"
            return

        #start a loop for paging
        i = True
        counter = 1
        while i == True:
            print "Working on page: " + str(counter)
            counter += 1
                
            #extract posts
            for post in main_dic['data']:

                created_time = post['created_time']
                if int(self.lastday) > created_time:
                    print "Done with: " + page
                    return
                created_time = str(created_time)
                
                #get the type of post, time, and post id
                kind = post['type'].encode('utf-8')
                post_id = post['id'].encode('utf-8')
                
                #get the message
                if "message" in post.keys():
                    message = post['message'].encode('utf-8')
                    message = regex.sub('\t|\n|\r|\"',"",message)                
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
                f.write(post_id + '\t' + pagename + '\t' + pageid  + '\t' + message + '\t' + kind + '\t')
                f.write(created_time + '\t' + shares + '\t' +  likes + '\t' +  comments + '\t' + link + '\n')
            
            #determin to continue
            nextpage =  main_dic['paging']['next'].encode('utf-8')
            response = urllib2.urlopen(nextpage)
            main_dic = json.load(response)
            if 'data' not in main_dic.keys():
                print "No data for page: " + page
                return

    def get_likes(self, post_ids):

        f = open(self.engagement_bank,'a')

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
                    f.write(post_id + '\t' + "#" + liker['id'].encode('utf-8') + '\t' + "like" + '\t' + "" + '\t' + "" + '\n')

                #get the totals on the first run and check to see if there is a next
                if "next" not in likes_dic.keys():
                    is_next = False
                else:
                    response = urllib2.urlopen(likes_dic['next'])
        f.close()


    def get_comments(self, post_ids):

        f = open(self.engagement_bank,'a')
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
                        message = re.sub('\t|\n|\r|"',"",message)
                        f.write(post_id + '\t' + "#" + str(commenter['from']['id']) + '\t' + "comment" + '\t' + str(commenter['created_time']) + '\t' + message + '\n')
                            
                    except:
                        print message
                    
        f.close()
        
                
if __name__ == '__main__':

    postname = sys.argv[1:][0]
    instance = FPA("CAACEdEose0cBAPRf8ngxAuYOh39l9jrZC14qxSnUOAZCuyPB1kCNnNxAOh4qd7WuLt1sdeugDlnkZCrkZBvOpFFhqYNhl76zM4gzNlEiq121CAZAMWYKKOnQkFVgxwZCw6egrNKHrlMp3aZAyCg63JZA7l3kJFiedyAfy5yZBxqcspjHZChi8HL6PZBTd3PrYxmFUQZD") 
    instance.initmainfile("Ukraine_search_april7.txt")    
    instance.limit = "30"
    instance.lastday = "1394755200"

    f = open("DOSAccounts.txt","r")
    for line in f:
        line = regex.sub("\n|\r","",line)
        instance.getposts(line)


    #instance.initengagmentbank()
    #instance.get_comments(["26365096875_10151932892141876",'10151932892141876_29592971',"10151932892141876_29592484"])
    #instance.get_likes(["26365096875_10151932892141876",'10151932892141876_29592971',"10151932892141876_29592484"])
