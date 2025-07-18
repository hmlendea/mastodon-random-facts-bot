import os.path
import sys
import re

import base64
import hashlib

import random

from mastodon import Mastodon
import requests

import text_replacements
import dynamic_tags

from fake_useragent import UserAgent

facts_file_path = sys.argv[1]
mastodon_instance = sys.argv[2]
mastodon_username = sys.argv[3]
mastodon_access_token = sys.argv[4]
tags_to_add = sys.argv[5]
language = sys.argv[6]

if not os.path.isfile("app_" + mastodon_instance + '.secret'):
    if Mastodon.create_app(
        mastodon_username,
        api_base_url = 'https://' + mastodon_instance,
        to_file = "app_" + mastodon_instance + '.secret'
    ):
        print('Successfully created the application on instance ' + mastodon_instance)
    else:
        print('Failed to create the application on instance ' + mastodon_instance)
        sys.exit(1)

try:
    mastodon_api = Mastodon(
        access_token = mastodon_access_token,
        api_base_url = 'https://' + mastodon_instance
    )
except Exception as ex:
    print("ERROR: Failed to log " + mastodon_username + " into " + mastodon_instance + ": " + ex)
    sys.exit(2)

try:
    with open(facts_file_path, "r") as file:
        facts = file.readlines()
except:
    print("ERROR: Failed to read the file: " + facts_file_path)
    sys.exit(1)

random_fact = None
while random_fact is None:
    random_fact = random.choice(facts)

media_urls = []
for p in re.finditer(r"https://[a-zA-Z0-9%\./_\-]*", random_fact):
    media_url = p.group(0)

    if (media_url.endswith('.gif') or
        media_url.endswith('.jpg') or
        media_url.endswith('.jpeg') or
        media_url.endswith('.png') or
        media_url.endswith('.webp')):
        print("URL " + media_url)
        media_urls.append(media_url)

toot_media = []
for media_url in media_urls:
    if media_url is None or media_url == 'None' or media_url == '':
        continue

    try:
        random_fact = random_fact.replace(media_url, '')

        print (' > Uploading media to Mastodon: ' + media_url)
        user_agent = UserAgent().firefox
        headers = {'User-Agent': user_agent}
        media = requests.get(media_url, headers=headers)
        media.raise_for_status()

        media_posted = mastodon_api.media_post(
            media.content,
            mime_type = media.headers.get('content-type'))
        toot_media.append(media_posted['id'])
        print('   > SUCCESS! ' + str(media_posted['id']))
    except Exception as ex:
        print('   > FAILURE! ' + str(ex))
        raise

random_fact = random_fact.lstrip().rstrip()
toot_body = text_replacements.apply(random_fact, language)
toot_body = toot_body.replace(r'\n', '\n')
toot_body = re.sub(r'\ \ *', ' ', toot_body)

all_tags_to_add = ''
dynamic_tags_to_add = dynamic_tags.get(toot_body, language)

if tags_to_add: all_tags_to_add += ' ' + tags_to_add
if dynamic_tags_to_add: all_tags_to_add += ' ' + dynamic_tags_to_add

if all_tags_to_add != '':
    filtered_tags_to_add = ''

    for tag in all_tags_to_add.split(' '):
        if '#' not in tag:
            filtered_tags_to_add += ' ' + tag
            continue

        if (tag.lower() + ' ' not in toot_body.lower() + ' ' and
            tag.lower() + ' ' not in filtered_tags_to_add.lower() + ' '):
            filtered_tags_to_add += ' ' + tag

    toot_body += '\n\n' + filtered_tags_to_add.strip()

print(' > Posting fact:\n' + random_fact)
mastodon_api.status_post(
    toot_body,
    in_reply_to_id = None,
    media_ids = toot_media,
    sensitive = False,
    visibility = 'public',
    spoiler_text = None)
