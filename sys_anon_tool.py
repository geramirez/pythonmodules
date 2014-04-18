# encoding: utf-8
import datetime
import random
import csv
from math import sqrt
from time import mktime
from time import strptime
import re

class sys_anonymizer:
    def __init__(self,files):
        #this function inits the tool
        self.files = files
        self.cipher = self.cipher()
    
    def cipher(self):
        #this fucntion create a secret cipher
        now = datetime.datetime.now()
        random.seed(now.day + now.year + now.month)
    
        alpha13 = ['z','x','c','v','b','n','m','a','s','d',
        'f','g','h','j','k','l','q','w','e','r','t','y','u',
        'i','o','p','0','9','8','7','6','5','4','3','2','1']
        
        random.shuffle(alpha13)
        alpha13 = "".join(alpha13)
        extra5 = random.randrange(10000,99999)
        return [alpha13,extra5]
        
        
    def encoder(self,user):
        #this encodes the text based on the cipher
    
        #standardize all
        user = re.sub("@","",user).lower()
        
        #check to see if the user is in the list
        if user in self.exceptions:
            return user
        else:
            pass
    
        #break the codes into 2 comps
        cipher = self.cipher[0]
        extra5 = self.cipher[1]
        
        user = user.lower()
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

    def anonymize_row(self,line):
                
        tweetdict = {}
        tweetdict['time'] = str(mktime(strptime(line[6], '%d %b %Y %H:%M:%S')))
        tweetdict['from_user'] =   self.encoder("@" + line[8])
        tweetdict['auth'] = line[11]
        tweetdict['followers'] = line[11]
        tweetdict['followers'] = line[12]
        tweetdict['following'] = line[13]
        tweetdict['gender'] = line[15]
        tweetdict['language'] = line[16]
        tweetdict['country'] = line[17]
        tweetdict['sentiment'] = line[21]
        tweetdict['gender'] = line[15]
        tweetdict['id'] = "#" + str(line[33])
        tweetdict['text'] = line[26]
                
        #parse text
        tweetdict['at_users'] = re.findall('@\w+',tweetdict['text'])
        tweetdict['rt_users'] = re.findall('(?<=RT )@\w+',tweetdict['text'])
        tweetdict['urls'] = re.findall('http://\w+\.\w+/.\w+',tweetdict['text'])
        tweetdict['hashtags'] = filter(lambda x: "#" in x, \
                            re.split("[ \\\"\'\.\,\-\:“”()!&\[\]]",tweetdict['text']))  
        
        #anonymize the text
        if tweetdict['at_users'] != []:
            for user in tweetdict['at_users']:
                tweetdict['text'] = re.sub(user,self.encoder(user),tweetdict['text'])

        with open(self.outputfile,'ab') as csvfile:
            output = csv.writer(csvfile)
            output.writerow(['tweet',''] + tweetdict.values())
                        
            if tweetdict['at_users'] != []:
                for connection in tweetdict['at_users']:
                    output.writerow(['user',connection] + tweetdict.values())

            if tweetdict['urls'] != []:
                for connection in tweetdict['urls']:
                    output.writerow(['url',connection] + tweetdict.values())

            if tweetdict['hashtags'] != []:
                for connection in tweetdict['hashtags']:
                    output.writerow(['hashtag',connection] + tweetdict.values())
                      

    def anonymize_files(self):
        #begin the process by looping the the files
        for _file in self.files:
            #open each file
            with open(_file,'rb') as f:
                content = csv.reader(f)
                for row in content:
                    #only anon rows that match description
                    if len(row) > 10:
                        if row[0] != "No.":
                            self.anonymize_row(row)


    def create_outputfile(self,outputfile="output.csv"):
        self.outputfile = outputfile
        with open(self.outputfile,'wb') as csvfile:
            writefile = csv.writer(csvfile)
            writefile.writerow(
            ['type','connection','rt_users', 'sentiment', 'language', \
            'gender', 'at_users', 'time', 'hashtags', \
            'auth', 'followers', 'urls', 'from_user', \
            'following', 'country', 'text', 'id'])

    def init_exceptionslist(self,filename='dosholder.txt'):
        
        self.exceptions = []
        with open(filename, 'rb') as csvfile:
            for row in csvfile:
                self.exceptions += [re.sub("\W","",row)]
        
        

if __name__ == '__main__':
    files = ['anon_test.csv']
    instance = sys_anonymizer(files)
    print instance.init_exceptionslist()
    instance.create_outputfile()
    instance.anonymize_files()
