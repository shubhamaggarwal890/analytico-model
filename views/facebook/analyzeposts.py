import facebook
import requests


def setup_facebook(token):
    return facebook.GraphAPI(access_token=token, version="2.12")


def get_facebook_posts(graph):
    fb_posts = []
    posts = {}
    try:
        posts = graph.get_object(id='me', fields='posts')
    except facebook.GraphAPIError as error:
        print(error)

    if posts.get('posts'):
        posts = posts.get('posts')
    else:
        return fb_posts
    i = 0
    while i < 30:
        try:
            if posts.get('data'):
                for post in posts['data']:
                    message = post.get('message')
                    if message:
                        hashtags = get_hashtags_from_text(message)
                        fb_posts.append({'post': message, 'hashtags': hashtags,
                                         'hashtag_count': len(hashtags)})
                        i = i + 1
            posts = requests.get(posts['paging']['next']).json()
        except KeyError or Exception as error:
            print(error)
            break
    return fb_posts


def get_facebook_friends(graph):
    friends = graph.get_object(id='me', fields='friends')
    if friends.get("friends") and friends.get('friends').get('summary'):
        return friends.get('friends').get('summary').get('total_count')
    return None


def get_hashtags_from_text(post):
    hashtags = []
    for tag in post.split():
        if tag.startswith("#"):
            hashtags.append({'name': tag})
    return hashtags
