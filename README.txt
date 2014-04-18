Okay, so basically this is the module I use for collecting raw social network data from Twitter. 
For network analysis I use another script built for iGraph in R. I�m hoping to continue building this module so that it feeds the data directly to networkX and maybe something that stores everything in MongoDB or CouchDB, something cool like that. 

Oh yeah, you can use as many consumer keys and secrets you want with this script. Just create a txt file called �consumer_keys.txt� setup like this:
consumer_key,consumer_secret,access_token_key,access_token_secret
consumer_key,consumer_secret,access_token_key,access_token_secret
�Use at your own risk. 

Here�s how this works:

#if true the output will be anonymized if false it will not
instance = twitterapi(True)
#set export file
instance.initexportfile(filename=�filename.csv�)
 #get keys
instance.getkeys()
#set search term        
instance.search("github")

-------
helpers.py are data munging function for small tasks
