import re
from urllib.parse import quote_plus
from urllib.request import urlopen
from urllib.error import *
import json
from ..tokens.tokens import QUORA_REQUEST_TOKEN as REQUEST_TOKEN


def scrap_quora_page(search_query):
    try:
        url = quote_plus('https://www.quora.com/search?q=' + search_query)
        handler = urlopen('https://api.proxycrawl.com/?token=' + REQUEST_TOKEN + '&scraper=quora-serp&url=' + url)
        return json.loads(handler.read().decode('utf8'))
    except HTTPError or Exception as error:
        print(error)
        return {}


def scrape_quora_question(question):
    try:
        url = quote_plus('https://www.quora.com/' + question)
        handler = urlopen('https://api.proxycrawl.com/?token=' + REQUEST_TOKEN + '&scraper=quora-question&url=' + url)
        return json.loads(handler.read().decode('utf8'))
    except HTTPError or Exception as error:
        print(error)
        return {}


def convert_special_character(question):
    question = question.strip()
    question = re.sub(r'[ \t]+', '-', question)
    question = re.sub(r'[^A-Za-z0-9-]+', '', question)
    return re.sub(r'[-]+', '-', question)
