import os.path
import sys

import base64
import hashlib

import random

from mastodon import Mastodon

import text_replacements

facts_file_path = sys.argv[1]
mastodon_instance = sys.argv[2]
mastodon_username = sys.argv[3]
mastodon_email_address = sys.argv[4].lower()
mastodon_password = base64.b64decode(sys.argv[5]).decode("utf-8")
tags_to_add = sys.argv[6]

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
        client_id = "app_" + mastodon_instance + '.secret',
        api_base_url = 'https://' + mastodon_instance
    )
    mastodon_api.log_in(
        mastodon_email_address,
        password = mastodon_password,
        scopes = ['read', 'write'],
        to_file = "app_" + mastodon_username + "@" + mastodon_instance + ".secret"
    )
except:
    print("ERROR: Failed to log " + mastodon_username + " into " + mastodon_instance)
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

toot_body = text_replacements.apply(random_fact)

if tags_to_add:
    toot_body += '\n\n' + tags_to_add

print('Posting fact: ' + random_fact)
mastodon_api.status_post(
    toot_body,
    in_reply_to_id = None,
    media_ids = None,
    sensitive = False,
    visibility = 'public',
    spoiler_text = None)
