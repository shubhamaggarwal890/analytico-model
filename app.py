from flask import Flask
import nltk
from views.views import *
import os
from views.sentimental import sentimental
from views.interrogative import interrogative
from views.news import news


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.add_url_rule('/index',   'index',  index)
app.add_url_rule('/twitter_analysis',   'analyze_twitter',  analyze_twitter,    methods=['POST'])
app.add_url_rule('/facebook_analysis',  'analyze_facebook', analyze_facebook,   methods=['POST'])
app.add_url_rule('/quora_analysis',     'analyze_quora',    analyze_quora,      methods=['POST'])
app.add_url_rule('/reddit_analysis',    'analyze_reddit',   analyze_reddit,     methods=['POST'])


if __name__ == '__main__':
    nltk.download('stopwords')
    s_modal_path = os.path.join(basedir, 'models/sentiment.sav')
    i_modal_path = os.path.join(basedir, 'models/interrogative.sav')
    n_modal_path = os.path.join(basedir, 'models/news.sav')
    s_pipeline = sentimental.model_load(s_modal_path)
    i_pipeline = interrogative.model_load(i_modal_path)
    n_pipeline = news.model_load(n_modal_path)

    set_sentimental_pipeline(s_pipeline)
    set_interrogative_pipeline(i_pipeline)
    set_news_pipeline(n_pipeline)
    app.run(host='0.0.0.0', debug=True)
