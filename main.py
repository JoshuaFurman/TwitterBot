# Written by: Joshua Furman

import tweepy
from tqdm import tqdm, trange
import Keys
import random
import time

def create_api():
    """Initialize the tweepy api"""

    auth = tweepy.OAuthHandler(Keys.CONSUMER_KEY, Keys.CONSUMER_SECRET)
    auth.set_access_token(Keys.ACCESS_TOKEN, Keys.ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        raise e
    return api

def add_user(newUsername):
    """Adds a user's id to the text file"""

    with open('ListOfUsers.txt', 'a') as userFile:
        userFile.write(f'{newUsername}')
        userFile.write('\n')

def load_users(fileName):
    """Returns a set containing all the users that have been retweeted"""
    users = []

    with open(fileName, 'r') as readFile:
        users = readFile.readlines()

    users = [name.strip(' \n') for name in users] # Clean the usernames

    return set(users)

def main():
    api = create_api()

    # Load list of users that have been retweeted
    retweetedUsers = load_users('ListOfUsers.txt')  # is a set
    
    while True:
        try:
            # Get the list of all users that retweeted the tweet. List comprehension to convert to strings
            allRTers = set([str(id) for id in api.retweeters(id=Keys.TWEET_ID)]) # is a set
            
            # Create a set containing only the new retweeters
            newUsers = allRTers.symmetric_difference(retweetedUsers)

            if len(newUsers) == 0:
                print()
                print('No new users have been found!')
                print('Resting....') # Wait for 2 minutes to scrap retweeters again
                for i in trange(120):
                    time.sleep(1)
                continue

            for user in newUsers:
                # Add new username to list of reweeted users and add to file
                retweetedUsers.add(str(user))
                add_user(str(user))

                # Get the users tweets
                tweetIds = []

                print()
                print('Searching user\'s tweets....')
                
                # Search a user's timeline and save tweetIds to a list
                for tweet in tqdm(tweepy.Cursor(api.user_timeline, id=user, include_rts=False).items()):
                    tweetIds.append(str(tweet.id))

                # Retweet random tweet and print to console
                api.retweet(random.choice(tweetIds))
                print(f'*BOOM retweet BOOM*')

        except tweepy.TweepError as message:
            print(f'There was an error:\n*{message}*')
        

if __name__ == "__main__":
    main()
