#!/usr/bin/env python3
import os
import time
from datetime import datetime
from email.utils import parsedate
import json
import glob
import argparse
import tweepy

def make_path(path):
    if not os.path.exists(path):
        print(f"creating {path}")
        os.makedirs(path)

def parse_date(str_date):
    return datetime(*(parsedate(str_date)[:6]))

def download_profile(username, profile_file, api):
    if not os.path.exists(profile_file):
        print(f"fetching profile for {username} ...")
        profile = api.get_user(username)
        profile = profile._json
        with open(profile_file, 'w+t') as fp:
            json.dump(profile, fp, indent=4, sort_keys=True)

def count_tweets(tweets_path):
    return len(glob.glob(f"{tweets_path}/*.json"))

def save_tweet(tweets_path, tweet):
    tweet_filename = f"{tweet.created_at}_{tweet.id}.json"
    tweet_filename = tweet_filename.replace(' ', '_')
    tweet_filename = f"{tweets_path}/{tweet_filename}"

    with open(tweet_filename, 'w+t') as fp:
        json.dump(tweet._json, fp)

    print(f"saved {tweet_filename}")

parser = argparse.ArgumentParser()

parser.add_argument("--consumer_key", help="API consumer key.", required=True)
parser.add_argument("--consumer_secret", help="API consumer secret.", required=True)
parser.add_argument("--access_token", help="API access token.", required=True)
parser.add_argument("--access_token_secret", help="API access token secret.", required=True)

parser.add_argument("--seed", help="File with profile names.", required=True)
parser.add_argument("--output", help="Output path.", default='output')
parser.add_argument("--limit", help="Number of statuses to download for each account.", type=int, default=500)
parser.add_argument("--delay", help="Number of seconds to wait when API rate limit is reached.", type=int, default=900)

args = parser.parse_args()

usernames = [] 

with open( args.seed, 'rt') as fp:
    for line in fp:
        line = line.strip()
        if line != "":
            usernames.append(line.lower())

usernames = set(usernames)

print("loaded %d user names from %s" % (len(usernames), args.seed))

auth = tweepy.OAuthHandler(args.consumer_key, args.consumer_secret)
auth.set_access_token(args.access_token, args.access_token_secret)
api = tweepy.API(auth)

for username in usernames:
    profile_path = os.path.join(args.output, username)
    profile_file = os.path.join(profile_path, 'profile.json')
    tweets_path  = os.path.join(profile_path, 'tweets')
    user_done    = False

    make_path(tweets_path)

    while not user_done:
        try:
            download_profile(username, profile_file, api)

            if count_tweets(tweets_path) >= args.limit:
                user_done = True
                break

            cursor = tweepy.Cursor(api.user_timeline, id=username).items(args.limit)
            while True:
                try:
                    save_tweet(tweets_path, cursor.next())
                except StopIteration:
                    break

            user_done = True
        except tweepy.TweepError as e:
             # user not found or suspended: 
            if 'status code = 401' in str(e) or 'status code = 404' in str(e) or e.api_code == 50 or e.api_code == 63:
                print(e)
                user_done = True
                break
            else:
                print("sleeping for %d seconds (%s)" % (args.delay, e))
                time.sleep(args.delay)