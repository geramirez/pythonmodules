Okay, so basically these are some of the modules/tools that I use for collecting raw social network data from Twitter. 
For network analysis I use another script built for iGraph in R.

###getnetv1###
This modules works with the Twitter API. You can use as many consumer keys and secrets you want with this script. Just create a txt file called consumer_keys.txt setup like this:
consumer_key,consumer_secret,access_token_key,access_token_secret
consumer_key,consumer_secret,access_token_key,access_token_secret
Use at your own risk. 

Here's how this works:
#if true the output will be anonymized if false it will not
instance = twitterapi(True)
#set export file
instance.initexportfile(filename="filename.csv")
 #get keys
instance.getkeys()
#set search term        
instance.search("github")

###helpers.py###
These are data munging function for small tasks, like quickly calculating network density. They only work with numpy or Pandas.

###sys_anon_tool###
This tool anonymizes and munges twitter data from a data provider. It's built to work with Python 2.* so the regex sucks and is drawn out.
