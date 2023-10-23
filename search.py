#!/usr/bin/env python3
import os
import sys
import json
import glob
from searchtweets import load_credentials, gen_rule_payload, collect_results

if len(sys.argv) < 3:
    print(f"usage: {sys.argv[0]} <screen name> <path>")
    quit()

screen_name = sys.argv[1].lower()
profile_path = os.path.join(sys.argv[2], screen_name)

if not os.path.exists(profile_path):
    print(f"creating {profile_path}")
    os.makedirs(profile_path)

creds = load_credentials("creds.yaml", yaml_key="search_tweets_api", env_overwrite=False)

rule = gen_rule_payload(f"from:{screen_name}", results_per_call=500)


tweets = collect_results(rule,
                         max_results=500,
                         result_stream_args=creds)

profile_file = os.path.join(profile_path, 'profile.json')
tweets_path = os.path.join(profile_path, 'tweets')

if not os.path.exists(tweets_path):
    print(f"creating {tweets_path}")
    os.makedirs(tweets_path)

for tweet in tweets:
    if not os.path.exists(profile_file):
        print(f"creating {profile_file}")
        with open(profile_file, 'w+t') as fp:
            json.dump(tweet['user'], fp)

    tweet_filename = f"{tweet['created_at']}_{tweet['id']}.json"
    tweet_filename = tweet_filename.replace(' ', '_')
    tweet_filename = os.path.join(tweets_path, tweet_filename)

    print(f"saving {tweet_filename}")
    with open(tweet_filename, 'w+t') as fp:
        json.dump(tweet, fp)
