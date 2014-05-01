#helpers

import regex
from pandas import ExcelWriter

def count_uniques(df):
    return df.drop_duplicates().count()

def potentials(network):
    n = len(set(network.connection.tolist() + network.from_user.tolist()))
    return n*(n-1)/2.0

def replacer(user,key):
    if user in key.keys():
        return regex.sub("\n|\r","",key[user])
    else: 
        return user

def text_replacer(text,users):

    for user in users.keys():
        text = regex.sub(user,users[user],text)

    return text
    
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

def pandas_to_edgelist(row):
    #this function generates an edge list for networkx
    return (row.connection,
            row.from_user,
            {"tweets":[{"id":row.id,
                      "text":row.text,
                      "hashtags":row.hashtags,
                      "favorite_count":row.favorite_count,
                      "in_reply_to_screen_name":row.in_reply_to_screen_name,
                      "retweet_count":row.retweet_count,
                      "media_type":row.media_type,
                      "media_url":row.media_url,
                      "user_mentions":row.user_mentions,
                      "lang":row.lang,
                      "in_reply_to_status_id_str":row.in_reply_to_status_id_str,
                      "url":row.url,
                      "created_at":row.created_at
                    }]}
            )

def pandas_to_edgelist_uni(row):
    #this function generates an edge list for networkx
    return (row.connection,
            row.from_user)

def pandas_node_attributes(row):
    #this function generates an edge list for networkx
    return (row.from_user, 
           {'user_lang' : row.user_lang,
            'user_utc_offset': row.user_utc_offset,
            'followers' : row.followers,
            #'user_created_time' : row.user_created_time,
            'user_statuses' : row.user_statuses,
            'time_zone' : row.time_zone
            }
            )

def save_xls(list_dfs, xls_path):
    writer = ExcelWriter(xls_path)
    for n, df in enumerate(list_dfs):
        df.to_excel(writer,'sheet%s' % n)
    writer.save()
