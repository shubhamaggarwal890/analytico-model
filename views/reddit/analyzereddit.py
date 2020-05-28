import praw
import prawcore

from ..tokens.tokens import REDDIT_CLIENT_ID as CLIENT_ID, REDDIT_CLIENT_SECRET as CLIENT_SECRET, \
    REDDIT_USER_AGENT as USER_AGENT


def get_subreddit_hot(reddit_api, subreddit, count, check_comments):
    posts = []
    try:
        for submission in reddit_api.subreddit(subreddit).hot(limit=count):
            post = {'author': submission.author.name, 'post': submission.selftext,
                    'link': submission.url, 'ups': submission.ups, 'comments': [],
                    'comments_count': len(submission.comments)}
            if check_comments:
                for comment in submission.comments:
                    try:
                        post['comments'].append({'author': comment.author.name, 'comment': comment.body,
                                                 'controversial': comment.controversiality, 'ups': comment.ups})
                    except AttributeError or Exception as error:
                        print(comment)

            posts.append(post)
    except prawcore.exceptions.Redirect or Exception:
        pass
    return posts


def setup_reddit():
    return praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
