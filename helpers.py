#helpers

import regex

def count_uniques(df):
    return df.drop_duplicates().count()

def potentials(network):
    n = len(set(network.connection.tolist() + network.from_user.tolist()))
    return n*(n-1)/2.0

def replacer(user,key):
    if user in key.keys():
        return key[user]
    else: 
        return user
    
def is_in_tweet_bank(tweet,tweetbank):
    for searchstring in tweetbank:
        if regex.findall(searchstring,tweet) != []:
            return True   
    return False

def is_in_user_bank(user,userbank):
    for searchstring in userbank:
        if user.lower() == searchstring.lower():
            return True  
    return False

def is_in_user_bank_sigdos(user,userbank):
    for searchstring in userbank:
        if regex.sub("\W","",user) == regex.sub("\W","",searchstring):
            return user
    return "@" + user
