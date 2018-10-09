import tweepy
import datetime
from time import sleep as original_sleep
from time import gmtime, strftime
from datetime import datetime, timedelta
from random import gauss
import random

#25/07/2017
#Feature Bot
#This bot is a compilation of different features.

class Bot:
   
    def __init__(self):
        self.consumer_key=''
        self.consumer_secret=''
        self.access_token=''
        self.access_token_secret=''
     
        self.api = self.authenticate()
        self.user_list = []
        
###############################################    
    def randomize_time(self,mean):
        #To appear less bot like, i've turned the cooldown into a bellcurve
        #This means what ever you put as the parameter is the highest value on the curve
        #Sleep picks a value on this curve as the time value, meaning you never get the same time value again and again.
        
        allowed_range = mean * 0.5
        stdev = allowed_range / 3  

        t = 0
        while abs(mean - t) > allowed_range:
            t = gauss(mean, stdev)

        return t


    def sleep(self,t):
        #original sleep is 'sleep()' from time module.
        original_sleep(self.randomize_time(t))
         
###############################################   
        
    def authenticate(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        
        try:
            api.verify_credentials()
        except:
            print("bot was unable to verify your login.")
        else:
            print("The bot was able to authenticate your login.")
            return api    
			
###############################################

    def search_twitter(self):
        #follows, retweets, and likes posts and users based on your specifications
        tagInput = input("Specify a tag:") #ask for a tag
        tNumInput = input("Number of posts:") #ask how many posts it should sweep
        tweetCount = 0 
        count403 = 0
        
        likeInput = input("Like posts Y/N?")
        reInput = input("Retweet posts Y/N?")
        fInput = input("Follow posters Y/N?")
        
        if "y" in likeInput:
            likePosts = True
        else:
            likePosts = False
        
        if "y" in reInput:
            retweetPosts = True
        else:
            retweetPosts = False
            
        if "y" in fInput:
            followPosts = True
        else:
            followPosts = False   
        
        for tweet in tweepy.Cursor(self.api.search,q=tagInput,lang='en').items(): 
            try:
                if tweetCount < (int(tNumInput)):   
                    print('----------------------')
                    print('Found tweet by: @' + tweet.user.screen_name) 
                    
                    if retweetPosts == True :
                        tweet.retweet()
                        print('Retweeted @' + tweet.user.screen_name) 
                  
                    if likeInput == True:
                        tweet.favorite()
                        print('Liked @' + tweet.user.screen_name) 
                  
                    if followPosts == True:
                        self.api.create_friendship(tweet.user.screen_name)
                        print('Followed: @' + tweet.user.screen_name) 
                   
                    tweetCount +=1
                    print(tweetCount)
                  
                    self.sleep(5)
            
            except tweepy.TweepError as e:
                print(e.reason)
                if "403" in e.reason: #a 403 error occurs if there are too many server requests. If you get a bunch, take a break
                    if count403 > 15:
                        print("There are too many 403 errors. Pausing for 30 mins")
                        self.sleep(1800)
                    else:
                        count403 += 1
                        print("Another 403 error. Total: " + str(count403))
                        self.sleep(1)
                else:
                    self.sleep(1) 
                
                continue
            except StopIteration:
                break
          
    def follow_others_followers(self):
        #follows a specified users followers
        userInput = input("Specify a user:")
        self.grab_users_followers(userInput)
        self.mass_follow(self.user_list)
        
    def grab_users_followers(self,user):
        #grabs a list of followers of another account, puts them in list
        for page in tweepy.Cursor(self.api.followers_ids, user).pages():
            self.user_list.extend(page)
            self.sleep(5)
        print(len(self.user_list),'users in list.')
        
    def print_userlist_tofile(self,users):
        #output the list to a file
        for line in self.user_list:
            print(str(line))
            UserListFile = open("ACCTEST.txt",'a')
            UserListFile.write(str(line)+"\n")#write the user to the file
        
    def mass_follow(self,users):
        #follow people in the list,
        for user in users:
            if user not in self.api.friends_ids(USERID):
                self.api.create_friendship(user)
                print("You are now following @"+self.api.get_user(user).screen_name)
            else:
                print("Already Following @"+self.api.get_user(user).screen_name)
            
            self.sleep(5)
            
    def follow_from_file(self):
        #follow people from a list on a file
        UserListFile = open("ACCTest.txt",'r')
        users = UserListFile.readlines()
        for user in users:
            if user not in self.api.friends_ids(USERID):
                self.api.create_friendship(user)
                print("You are now following @"+self.api.get_user(user).screen_name)
            else:
                print("Already Following @"+self.api.get_user(user).screen_name) 
  
            self.sleep(5)
        
    def follow_followers(self):
        #follow back followers
         for follower in tweepy.Cursor(self.api.followers).items():
            if follower not in tweepy.Cursor(self.api.friends).items():
                follower.follow()
                print ('Followed: @'+ follower.screen_name)
                self.sleep(5)
                
    def follow_specific(self):
        #name a user to follow
         userInput = input("Specify a user:")
         
         for follower in tweepy.Cursor(self.api.followers).items():
            if follower not in tweepy.Cursor(self.api.friends).items():
                follower.follow()
                print ('Followed: @'+ follower.screen_name)
                self.sleep(5)
   
    def clear_timeline(self):
        #clears your tweets and retweets
            for status in tweepy.Cursor(self.api.user_timeline).items():
                try:
                    self.api.destroy_status(status.id)
                    #self.sleep(5)
                    print ("Deleted:", status.id)   
                except:
                    print ("Failed to delete:", status.id)
            
   
    def unfollow_unfollowers(self):
        #unfollow anyone who isnt following you
        try:
            for i in self.api.friends_ids(USERID):
                if i not in self.api.followers_ids(USERID):
                    print ("Unfollowing @" + (self.api.get_user(i).screen_name))
                    self.api.destroy_friendship(i)
                    self.sleep(5)
        except tweepy.TweepError as e:
                print(e.reason)
                if "88" in e.reason:
                    print("There are too many 88 errors. Pausing for 5 mins")
                    self.sleep(300)
                    self.unfollow_unfollowers()
                    print("ok")
                  
    def mass_unfollow(self):
        #unfollow all
        for i in self.api.friends_ids(USERID):
            print ("Unfollowing @" + (self.api.get_user(i).screen_name))
            self.api.destroy_friendship(i)
            self.sleep(5)
            
    def clear_likes(self):
        #unlikes posts youve liked
         for tweet in tweepy.Cursor(self.api.favorites).items():
              try:
                    self.api.destroy_favorite(tweet.id)
                    self.sleep(5)
                    print ("Unliking:", tweet.id)
              except:
                    print ("Failed to unlike:", tweet.id)
   
    def tweet(self):
        #tweets certain phrases off a file, 
        #It should be noted that you cannoot tweet the same exact phrase more than once...
        argfile = input("filename: ")
        filename = open(argfile,'r')
        f = filename.readlines()
        filename.close()
        
        for line in f:
            try:
                self.api.update_status(status = line)
                print("Tweeted: "+line)
                self.sleep(5)        
            except tweepy.TweepError as e:
                print(e.reason)
                continue
            except StopIteration:
                break
            
        
       
    def direct_message(self):
        #Incomplete
        followers = self.api.followers_ids()
        lastFollow = followers[0]
        print(followers[0])
        print("Checking for new followers...")
        self.api.send_direct_message("username", "Thank you for following me. Cheers!")
        self.sleep(30)
        Newfollowers = self.api.followers_ids()
        
        if Newfollowers[0] != lastFollow:
            
            i = (Newfollowers.index(lastFollow))
            print(i)
            for i in Newfollowers:
                if i > 0: 
                    self.api.send_direct_message("username", "Thank you for following me. Cheers!")
                    i -= 1
                else:
                    break;
                          
twitter_bot = Bot()

while True:
    print('-------------------------------------------------')
    print('Welcome to our bot, please select a command.')
    print('1 - Like, retweet, and follow users based on tag.')
    print('2 - Follow a specified users followers.')
    print('3 - Follow your followers.')
    print('4 - Unfollow those who arnt following you.')
    print('5 - Mass Unfollow.')
    print('6 - Clear timeline.')
    print('7 - Clear Likes.')
    print('8 - Direct message new followers.')
    print('9 - Auto Tweet')
    print('0 - Retweet Priority')
    
    command = input("Enter a command: ")
    
    if "1" in command:
        twitter_bot.search_twitter()
    elif "2" in command:
        twitter_bot.follow_others_followers() 
    elif "3" in command:
        twitter_bot.follow_followers()
    elif "4" in command:
        twitter_bot.unfollow_unfollowers()
    elif "5" in command:
        twitter_bot.mass_unfollow()
    elif "6" in command:
        twitter_bot.clear_timeline()
    elif "7" in command:
        twitter_bot.clear_likes()
    elif "8" in command:
        twitter_bot.direct_message()
    elif "9" in command:
        twitter_bot.tweet()
    elif "0" in command:
        twitter_bot.retweet_priority()
    elif "t" in command:
        twitter_bot.retweet_priority_list()
    else:
        break;
    
    
    
  