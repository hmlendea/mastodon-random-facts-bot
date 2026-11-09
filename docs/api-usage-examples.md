# API usage examples

This document provides concrete examples of the API calls the bot makes, for reference when debugging or extending integrations.

## Mastodon.py calls

### Application registration

```python
from mastodon import Mastodon

result = Mastodon.create_app(
    'mybot',
    api_base_url='https://mastodon.social',
    to_file='app_mastodon.social.secret'
)
# result is truthy on success, falsy on failure
```

### Client construction

```python
mastodon_api = Mastodon(
    access_token='USER_ACCESS_TOKEN',
    api_base_url='https://mastodon.social'
)
```

### Media upload

```python
import requests

media_url = 'https://example.com/image.png'
user_agent = 'Mozilla/5.0 (Firefox)'
headers = {'User-Agent': user_agent}

response = requests.get(media_url, headers=headers)
response.raise_for_status()

media_posted = mastodon_api.media_post(
    response.content,
    mime_type=response.headers.get('content-type')
)
# media_posted = {'id': '1234567890', 'type': 'image', 'url': '...', ...}
media_id = media_posted['id']
```

### Status publication

```python
toot_body = 'This is the fact text.\n\n #Fact #Random'
toot_media = ['1234567890', '1234567891']

status = mastodon_api.status_post(
    toot_body,
    in_reply_to_id=None,
    media_ids=toot_media,
    sensitive=False,
    visibility='public',
    spoiler_text=None
)
# status = {'id': '9876543210', 'content': '<p>This is the fact text.</p>...', ...}
```

## requests calls

### Media download with Firefox user agent

```python
from fake_useragent import UserAgent
import requests

ua = UserAgent()
headers = {'User-Agent': ua.firefox}

response = requests.get('https://example.com/image.png', headers=headers)
response.raise_for_status()

# response.content -> bytes
# response.headers.get('content-type') -> 'image/png'
```

## Operator hook calls

### text_replacements.apply

```python
# Called by entry point:
transformed = text_replacements.apply(
    'Romania is a country.\n\n #Fact',
    'ro'
)
# Expected return: '🇷🇴#Romania is a country.\n\n #Fact' (example)
```

### dynamic_tags.get

```python
# Called by entry point:
tags = dynamic_tags.get(
    '🇷🇴#Romania is a country.\n\n #Fact',
    'ro'
)
# Expected return: ' #Romania #Europe' or None
```

## Full pipeline trace

A successful run with one media URL produces this sequence:

```
1. Mastodon.create_app('mybot', 'https://mastodon.social', 'app_mastodon.social.secret')
2. Mastodon('TOKEN', 'https://mastodon.social')
3. open('facts.txt').readlines() -> ['Fact with https://img.png\n']
4. random.choice -> 'Fact with https://img.png\n'
5. re.finditer -> match 'https://img.png' (suffix .png)
6. random_fact.replace('https://img.png', '') -> 'Fact with \n'
7. UserAgent().firefox -> 'Mozilla/5.0 ...'
8. requests.get('https://img.png', headers={'User-Agent': '...'})
9. response.raise_for_status()
10. mastodon_api.media_post(response.content, 'image/png') -> {'id': '123'}
11. text_replacements.apply('Fact with ', 'en') -> 'Fact with '
12. 'Fact with '.replace(r'\n', '\n') -> 'Fact with '
13. re.sub(r'\ \ *', ' ', 'Fact with ') -> 'Fact with '
14. dynamic_tags.get('Fact with ', 'en') -> None
15. all_tags_to_add = ' #Fact #Random' (from CLI)
16. filter -> ' #Fact #Random' (no duplicates in body)
17. toot_body = 'Fact with \n\n #Fact #Random'
18. mastodon_api.status_post('Fact with \n\n #Fact #Random', None, ['123'], False, 'public', None)
```

## Error response shapes

### Mastodon.py exceptions

```python
from mastodon import MastodonError, MastodonNetworkError, MastodonAPIError

try:
    mastodon_api.status_post(...)
except MastodonNetworkError as e:
    # Connection error, timeout, DNS failure
    # e.args[0] contains the underlying requests exception
except MastodonAPIError as e:
    # HTTP error from Mastodon (4xx, 5xx)
    # e.error_dict contains the API error response
except MastodonError as e:
    # Base class for all Mastodon.py errors
```

### requests exceptions

```python
import requests

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.ConnectionError:
    # DNS failure, refused connection
except requests.Timeout:
    # Request timed out (no timeout configured by default)
except requests.HTTPError as e:
    # 4xx or 5xx response
    # e.response.status_code, e.response.text
except requests.RequestException as e:
    # Base class for all requests errors
```

## Minimal reproduction scripts

### Test application registration

```python
from mastodon import Mastodon
result = Mastodon.create_app('test', 'https://mastodon.social', 'test.secret')
print('Registration:', 'ok' if result else 'failed')
```

### Test media upload

```python
from mastodon import Mastodon
import requests

m = Mastodon(access_token='TOKEN', api_base_url='https://mastodon.social')
r = requests.get('https://example.com/test.png')
r.raise_for_status()
media = m.media_post(r.content, r.headers.get('content-type'))
print('Media ID:', media['id'])
```

### Test status post

```python
from mastodon import Mastodon

m = Mastodon(access_token='TOKEN', api_base_url='https://mastodon.social')
status = m.status_post('Test post', media_ids=[], visibility='public')
print('Status ID:', status['id'])
```