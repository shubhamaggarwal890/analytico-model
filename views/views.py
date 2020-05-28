from flask import request

from .facebook import analyzepage
from .facebook import analyzeposts
from .interrogative import interrogative
from .news import news
from .quora import analyzequora
from .reddit import analyzereddit
from .sentimental import sentimental
from .twitter import analyzetwitter

sentimental_pipeline = None
interrogative_pipeline = None
news_pipeline = None


def set_sentimental_pipeline(pipeline):
    global sentimental_pipeline
    sentimental_pipeline = pipeline


def set_news_pipeline(pipeline):
    global news_pipeline
    news_pipeline = pipeline


def set_interrogative_pipeline(pipeline):
    global interrogative_pipeline
    interrogative_pipeline = pipeline


def analyze_facebook_user(access_token):
    print('Fetching posts and friends for the user')
    graph = analyzeposts.setup_facebook(access_token)
    posts = analyzeposts.get_facebook_posts(graph)
    friends = analyzeposts.get_facebook_friends(graph)
    print('Fetching posts and friends for the user complete')

    return posts, friends


def analyze_facebook_page(page):
    print("Starting to fetch page posts from facebook")
    posts = analyzepage.facebook_login("https://mobile.facebook.com/" + page + "/")
    print("Complete fetching page posts from facebook")
    return posts


def analyze_twitter_tweets(twitter, name):
    tweets = analyzetwitter.get_user_timeline(twitter, name)
    return tweets


def analyze_twitter_hashtags(twitter, hashtags):
    hashtag_tweet = []
    for hashtag in hashtags:
        tweets = analyzetwitter.get_tweets_based_hashtag(twitter, hashtag)
        hashtag_tweet.extend(tweets)
    return hashtag_tweet


def analyze_quora_query(query):
    print("Starting to fetch query data from quora")
    quora_data = analyzequora.scrap_quora_page(query)
    results = []
    if quora_data and quora_data.get('body') and quora_data.get('body').get('questions'):
        for data in quora_data.get('body').get('questions'):
            if data.get('question'):
                result = {'question': data.get('question'), 'answer_count': data.get('answerCount'),
                          'link': data.get('questionLink')}
                answer = data.get('resultSnippet')
                if answer.get('answerAuthor'):
                    result['author'] = answer.get('answerAuthor')
                else:
                    result['author'] = 'Anonymous'
                try:
                    result['answer'] = answer.get('answer').get('text')[0]
                except IndexError:
                    result['answer'] = ''
                results.append(result)
    print("Finished fetching data from quora")
    return results


def analyze_quora_question(question):
    print("Fetching data based given question quora")
    quora_data = analyzequora.scrape_quora_question(analyzequora.convert_special_character(question))

    result = {}
    if quora_data and quora_data.get('body') and quora_data.get('body').get('question') and \
            quora_data.get('body').get('question').get('text'):
        data = quora_data.get('body').get('question')
        result = {'question': data.get('text'), 'answer_count': data.get('answerCount'),
                  'link': data.get('link')}
        answers = data.get('answers')
        result['answers'] = []
        for answer in answers:
            author = 'Anonymous'
            if answer.get('answerHeader') and answer.get('answerHeader').get('answerAuthor'):
                author = answer.get('answerHeader').get('answerAuthor')
            result['answers'].append({'author': author, 'answer': " ".join(answer.get('answerText'))})
    print("Finished fetching data from quora based question")
    if not result:
        return None
    return result


def analyze_reddit_post(reddit, subreddit, comment):
    posts = analyzereddit.get_subreddit_hot(reddit, subreddit, 30, comment)
    return posts


def analyze_twitter():
    twitter = analyzetwitter.setup_twitter()
    meta_data = request.json
    print(meta_data)
    analyzer = meta_data.get('analyzer')
    output = {}
    if meta_data.get('screen_name'):
        tweets = analyze_twitter_tweets(twitter, meta_data.get('screen_name'))
        for i in range(0, len(tweets)):
            if analyzer.get('sentimental'):
                tweets[i]['sentimental'] = sentimental_prediction(tweets[i].get('post'))
            if analyzer.get('question'):
                tweets[i]['question'] = interrogative_prediction(tweets[i].get('post'))
            if analyzer.get('news'):
                tweets[i]['news'] = news_prediction(tweets[i].get('post'))
        output['tweets'] = tweets
        information = analyzetwitter.get_user_data(twitter, meta_data.get('screen_name'))
        output['followers'] = information.get('followers')
        output['following'] = information.get('following')
    if meta_data.get('hashtags'):
        hashtags = [i.get('name') for i in meta_data.get('hashtags') if i.get('name')]
        tweets = analyze_twitter_hashtags(twitter, hashtags)
        for i in range(0, len(tweets)):
            if analyzer.get('sentimental'):
                tweets[i]['sentimental'] = sentimental_prediction(tweets[i].get('post'))
            if analyzer.get('question'):
                tweets[i]['question'] = interrogative_prediction(tweets[i].get('post'))
            if analyzer.get('news'):
                tweets[i]['news'] = news_prediction(tweets[i].get('post'))
        output['hashtags'] = tweets
    output['twitter'] = meta_data.get('twitter_id')
    output['email'] = meta_data.get('email')
    print(output)

    return output


def analyze_facebook():
    meta_data = request.json
    analyzer = meta_data.get('analyzer')
    output = {}
    if meta_data.get('token'):
        posts, friends = analyze_facebook_user(meta_data.get('token'))
        print('Starting analysis on the posts of the user')
        for i in range(0, len(posts)):
            if analyzer.get('sentimental'):
                posts[i]['sentimental'] = sentimental_prediction(posts[i].get('post'))
            if analyzer.get('question'):
                posts[i]['question'] = interrogative_prediction(posts[i].get('post'))
        output['posts'] = posts
        output['friends'] = friends
        print('Completed analysis on the posts of the user')

    if meta_data.get('page'):
        posts = analyze_facebook_page(meta_data.get('page'))
        print('Starting analysis on the page posts of the user')
        for i in range(0, len(posts)):
            if analyzer.get('sentimental'):
                posts[i]['sentimental'] = sentimental_prediction(posts[i].get('post'))
            if analyzer.get('question'):
                posts[i]['question'] = interrogative_prediction(posts[i].get('post'))
        output['page_post'] = posts
        print('Completed analysis on the page posts of the user')
    output['facebook'] = meta_data.get('user_id')
    output['email'] = meta_data.get('email')
    print(output)
    return output


def analyze_quora():
    meta_data = request.json
    analyzer = meta_data.get('analyzer')
    print(meta_data)
    output = {}
    if meta_data.get('query'):
        questions = analyze_quora_query(meta_data.get('query'))
        if analyzer.get('sentimental'):
            for i in range(0, len(questions)):
                questions[i]['sentimental'] = sentimental_prediction(questions[i].get('answer'))
        output['query'] = questions
    if meta_data.get('question'):
        answer = analyze_quora_question(meta_data.get('question'))
        if answer and answer.get('answers'):
            if analyzer.get('sentimental'):
                for i in range(0, len(answer.get('answers'))):
                    answer.get('answers')[i]['sentimental'] = sentimental_prediction(
                        answer.get('answers')[i].get('answer'))

        output['question'] = answer

    output['quora'] = meta_data.get('user_id')
    output['email'] = meta_data.get('email')
    print(output)
    return output


def analyze_reddit():
    reddit = analyzereddit.setup_reddit()
    meta_data = request.json
    analyzer = meta_data.get('analyzer')
    print(meta_data)
    output = {}
    if meta_data.get('subreddit'):
        if analyzer.get('comments'):
            print("Starting to fetch posts of user with comments")
            posts = analyze_reddit_post(reddit, meta_data.get('subreddit'), True)
            print("Posts and Comments fetched, Starting to do sentimental analysis")
            if analyzer.get('sentimental'):
                for i in range(0, len(posts)):
                    posts[i]['sentimental'] = sentimental_prediction(posts[i].get('post'))
                    for j in range(0, len(posts[i].get('comments'))):
                        posts[i].get('comments')[j]['sentimental'] = sentimental_prediction(posts[i].get(
                            'comments')[j].get('comment'))
            output['posts'] = posts
        else:
            print("Starting to fetch posts of user without  comments")
            posts = analyze_reddit_post(reddit, meta_data.get('subreddit'), False)
            print("Posts fetched, Starting to do sentimental analysis")
            if analyzer.get('sentimental'):
                for i in range(0, len(posts)):
                    posts[i]['sentiment'] = sentimental_prediction(posts[i].get('post'))
            output['posts'] = posts
    output['reddit'] = meta_data.get('user_id')
    output['email'] = meta_data.get('email')
    print(output)
    return output


def sentimental_prediction(text):
    global sentimental_pipeline
    return sentimental.prediction(text, sentimental_pipeline)


def interrogative_prediction(text):
    global interrogative_pipeline
    return interrogative.prediction(text, interrogative_pipeline)


def news_prediction(text):
    global news_pipeline
    return news.prediction(text, news_pipeline)


def index():
    return "Hello from flask"
