import os.path
import random
import re
import sys

from typing import List, Optional, Tuple

import requests
from fake_useragent import UserAgent
from mastodon import Mastodon

import dynamic_tags
import text_replacements
from config import (
    APPLICATION_REGISTRATION_FAILURE_EXIT_CODE,
    APPLICATION_SECRET_FILE_NAME_FORMAT,
    CONTENT_TYPE_HEADER_NAME,
    ESCAPED_NEWLINE_SEQUENCE,
    FACTS_FILE_PATH_ARGUMENT_INDEX,
    FACTS_FILE_READ_FAILURE_EXIT_CODE,
    HASHTAG_MARKER,
    LANGUAGE_ARGUMENT_INDEX,
    MASTODON_ACCESS_TOKEN_ARGUMENT_INDEX,
    MASTODON_API_BASE_URL_FORMAT,
    MASTODON_CLIENT_FAILURE_EXIT_CODE,
    MASTODON_INSTANCE_ARGUMENT_INDEX,
    MASTODON_USERNAME_ARGUMENT_INDEX,
    MEDIA_URL_PATTERN,
    NEWLINE_CHARACTER,
    SINGLE_SPACE,
    SPACE_RUN_PATTERN,
    STATUS_IS_SENSITIVE,
    STATUS_VISIBILITY,
    SUPPORTED_MEDIA_FILE_EXTENSIONS,
    TAG_BLOCK_SEPARATOR,
    TAG_SEPARATOR,
    TAGS_TO_ADD_ARGUMENT_INDEX,
    USER_AGENT_HEADER_NAME,
)


def read_arguments() -> Tuple[str, str, str, str, str, str]:
    facts_file_path = sys.argv[FACTS_FILE_PATH_ARGUMENT_INDEX]
    mastodon_instance = sys.argv[MASTODON_INSTANCE_ARGUMENT_INDEX]
    mastodon_username = sys.argv[MASTODON_USERNAME_ARGUMENT_INDEX]
    mastodon_access_token = sys.argv[MASTODON_ACCESS_TOKEN_ARGUMENT_INDEX]
    tags_to_add = sys.argv[TAGS_TO_ADD_ARGUMENT_INDEX]
    language = sys.argv[LANGUAGE_ARGUMENT_INDEX]

    return (facts_file_path, mastodon_instance, mastodon_username,
            mastodon_access_token, tags_to_add, language)


def ensure_application_registration(mastodon_instance: str, mastodon_username: str) -> None:
    secret_file_path = APPLICATION_SECRET_FILE_NAME_FORMAT.format(instance=mastodon_instance)

    if os.path.isfile(secret_file_path):
        return

    api_base_url = MASTODON_API_BASE_URL_FORMAT.format(instance=mastodon_instance)
    registered_application = Mastodon.create_app(
        mastodon_username,
        api_base_url=api_base_url,
        to_file=secret_file_path)

    if registered_application:
        print(f'Successfully created the application on instance {mastodon_instance}')

        return

    print(f'Failed to create the application on instance {mastodon_instance}')
    sys.exit(APPLICATION_REGISTRATION_FAILURE_EXIT_CODE)


def create_mastodon_client(mastodon_instance: str, mastodon_username: str, mastodon_access_token: str) -> Mastodon:
    mastodon_client = None

    try:
        mastodon_client = Mastodon(
            access_token=mastodon_access_token,
            api_base_url=MASTODON_API_BASE_URL_FORMAT.format(instance=mastodon_instance))
    except Exception as exception:
        print(f'ERROR: Failed to log {mastodon_username} into {mastodon_instance}: {exception}')
        sys.exit(MASTODON_CLIENT_FAILURE_EXIT_CODE)

    return mastodon_client


def read_facts(facts_file_path: str) -> List[str]:
    facts = None

    try:
        with open(facts_file_path, 'r') as facts_file:
            facts = facts_file.readlines()
    except Exception:
        print(f'ERROR: Failed to read the file: {facts_file_path}')
        sys.exit(FACTS_FILE_READ_FAILURE_EXIT_CODE)

    return facts


def select_random_fact(facts: List[str]) -> str:
    return random.choice(facts)


def extract_media_urls(fact: str) -> List[str]:
    media_urls = []

    for url_match in re.finditer(MEDIA_URL_PATTERN, fact):
        media_url = url_match.group(0)

        if media_url.endswith(SUPPORTED_MEDIA_FILE_EXTENSIONS):
            print(f'URL {media_url}')

            media_urls.append(media_url)

    return media_urls


def download_and_upload_media_item(mastodon_client: Mastodon, media_url: str) -> str:
    user_agent = UserAgent().firefox
    headers = {USER_AGENT_HEADER_NAME: user_agent}

    media_response = requests.get(media_url, headers=headers)
    media_response.raise_for_status()

    media_posted = mastodon_client.media_post(
        media_response.content,
        mime_type=media_response.headers.get(CONTENT_TYPE_HEADER_NAME))

    return media_posted['id']


def download_and_upload_media(mastodon_client: Mastodon, fact: str, media_urls: List[str]) -> Tuple[str, List[str]]:
    fact_without_media_urls = fact
    media_ids = []

    for media_url in media_urls:
        if media_url is None or media_url == 'None' or media_url == '':
            continue

        try:
            fact_without_media_urls = fact_without_media_urls.replace(media_url, '')
            print(f' > Uploading media to Mastodon: {media_url}')

            media_id = download_and_upload_media_item(mastodon_client, media_url)

            media_ids.append(media_id)
            print(f'   > SUCCESS! {media_id}')
        except Exception as exception:
            print(f'   > FAILURE! {exception}')

            raise

    return (fact_without_media_urls, media_ids)


def transform_fact_body(stripped_fact: str, language: str) -> str:
    transformed_body = text_replacements.apply(stripped_fact, language)
    transformed_body = transformed_body.replace(ESCAPED_NEWLINE_SEQUENCE, NEWLINE_CHARACTER)
    transformed_body = re.sub(SPACE_RUN_PATTERN, SINGLE_SPACE, transformed_body)

    return transformed_body


def filter_tags(all_tags_to_add: str, body: str) -> str:
    filtered_tags_to_add = ''

    for tag in all_tags_to_add.split(TAG_SEPARATOR):
        if HASHTAG_MARKER not in tag:
            filtered_tags_to_add += SINGLE_SPACE + tag

            continue

        if (tag.lower() + SINGLE_SPACE not in body.lower() + SINGLE_SPACE and
            tag.lower() + SINGLE_SPACE not in filtered_tags_to_add.lower() + SINGLE_SPACE):
            filtered_tags_to_add += SINGLE_SPACE + tag

    return filtered_tags_to_add


def build_tag_block(body: str, tags_to_add: str, language: str) -> Optional[str]:
    dynamic_tags_to_add = dynamic_tags.get(body, language)
    all_tags_to_add = ''

    if tags_to_add:
        all_tags_to_add += SINGLE_SPACE + tags_to_add

    if dynamic_tags_to_add:
        all_tags_to_add += SINGLE_SPACE + dynamic_tags_to_add

    if all_tags_to_add == '':
        return None

    filtered_tags_to_add = filter_tags(all_tags_to_add, body)

    return filtered_tags_to_add.strip()


def publish_status(mastodon_client: Mastodon, fact_text: str, body: str, media_ids: List[str]) -> None:
    print(f' > Posting fact:\n{fact_text}')

    mastodon_client.status_post(
        body,
        in_reply_to_id=None,
        media_ids=media_ids,
        sensitive=STATUS_IS_SENSITIVE,
        visibility=STATUS_VISIBILITY,
        spoiler_text=None)


def main() -> None:
    (facts_file_path, mastodon_instance, mastodon_username,
     mastodon_access_token, tags_to_add, language) = read_arguments()

    ensure_application_registration(mastodon_instance, mastodon_username)
    mastodon_client = create_mastodon_client(mastodon_instance, mastodon_username, mastodon_access_token)

    facts = read_facts(facts_file_path)
    selected_fact = select_random_fact(facts)

    media_urls = extract_media_urls(selected_fact)
    fact_text, media_ids = download_and_upload_media(mastodon_client, selected_fact, media_urls)

    stripped_fact = fact_text.strip()
    toot_body = transform_fact_body(stripped_fact, language)
    tag_block = build_tag_block(toot_body, tags_to_add, language)

    if tag_block is not None:
        toot_body += TAG_BLOCK_SEPARATOR + tag_block

    publish_status(mastodon_client, stripped_fact, toot_body, media_ids)


if __name__ == '__main__':
    main()
