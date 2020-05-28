import time

import requests
from bs4 import BeautifulSoup

from ..tokens.tokens import FACEBOOK_EMAIL_ID as EMAIL_ID, FACEBOOK_PASSWORD as PASSWORD


def get_beautiful_soup(session, url):
    r = None
    i = 0
    try:
        while i < 5:
            r = session.get(url)
            time.sleep(3)
            if r.ok:
                break
            i = i + 1
        return BeautifulSoup(r.text, 'lxml')
    except requests.HTTPError or Exception:
        return ""


def scrape_post(session, base_url, post_url):
    post_data = {}
    post_bs = get_beautiful_soup(session, base_url + post_url)
    time.sleep(5)
    try:
        post_text_element = post_bs.find('div', id='u_0_0').div
        string_groups = [p.strings for p in post_text_element.find_all('p')]
        text_list = "".join([repr(string) for group in string_groups for string in group]).replace("'", "")
        post_data = {'post': text_list}

    except AttributeError or Exception:
        post_data = {'post': ''}

    return post_data


def posts_completed(scraped_posts, limit):
    if len(scraped_posts) == limit:
        return True
    else:
        return False


def crawl_profile(session, base_url, profile_url, post_limit):
    profile_bs = get_beautiful_soup(session, profile_url)
    scraped_posts = 0
    scraped_posts_data = []

    while scraped_posts < post_limit:
        try:
            posts = profile_bs.find('div', id='recent').div.div.contents
        except AttributeError or Exception:
            return "Not valid"

        posts_urls = [a['href'] for a in profile_bs.find_all('a', text='Full Story')]

        for post_url in posts_urls:
            try:
                post_data = scrape_post(session, base_url, post_url)
                if post_data.get('post'):
                    hashtags = get_hashtags_from_text(post_data.get('post'))
                    post_data['hashtags'] = hashtags
                    post_data['hashtag_count'] = len(hashtags)
                    scraped_posts_data.append(post_data)
                    scraped_posts += 1
            except AttributeError or Exception as e:
                pass

            if posts_completed(scraped_posts_data, post_limit):
                break

        if not posts_completed(scraped_posts_data, post_limit):
            show_more_posts_url = profile_bs.find('div', id='recent').next_sibling.a['href']
            profile_bs = get_beautiful_soup(session, base_url + show_more_posts_url)
            time.sleep(3)
        else:
            break
    return scraped_posts_data


def facebook_login_check():
    base_url = 'https://mobile.facebook.com'
    session = requests.session()
    login_form_url = '/login/device-based/regular/login/?refsrc=https%3A%2F%2Fmobile.facebook.com%2Flogin' \
                     '%2Fdevice-based%2Fedit-user%2F&lwv=100'
    params = {'email': EMAIL_ID, 'pass': PASSWORD}
    logged_request = session.post(base_url + login_form_url, data=params)

    if logged_request.ok:
        return 'ok'
    else:
        return 'fail'


def facebook_login(profile):
    base_url = 'https://mobile.facebook.com'
    session = requests.session()
    login_form_url = '/login/device-based/regular/login/?refsrc=https%3A%2F%2Fmobile.facebook.com%2Flogin' \
                     '%2Fdevice-based%2Fedit-user%2F&lwv=100'
    params = {'email': EMAIL_ID, 'pass': PASSWORD}
    index = 0
    try:
        while True:
            if index > 10:
                break
            time.sleep(3)
            logged_request = session.post(base_url + login_form_url, data=params)
            if logged_request.ok:
                # logging.info('[*] Logged in.')
                break
            index += 1
    except requests.HTTPError or Exception:
        return []

    profile_posts = crawl_profile(session, base_url, profile, 2)
    return profile_posts


def get_hashtags_from_text(post):
    hashtags = []
    for tag in post.split():
        if tag.startswith("#"):
            hashtags.append({'name': tag})
    return hashtags
