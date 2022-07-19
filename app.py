from datetime import datetime
from sqlite3 import Cursor

import dotenv
import pymongo
import requests

from src.telegram.telegram import TelegramService
from src.util import extract_tags, fetch_content, get_keywords

BASE_URL = "https://www.tagesschau.de/api2"
NEWS_PATH = "/news"


class Article:
    def __init__(self, article_obj: object):
        self.id = article_obj["externalId"]
        self.title = article_obj["title"]
        self.date = datetime.fromisoformat(article_obj["date"])
        self.tracking = article_obj["tracking"]
        self.tags = extract_tags(article_obj["tags"])
        self.regionIds = article_obj["regionIds"]
        self.details = article_obj["details"]
        self.topline = article_obj["topline"]
        self.geotags = extract_tags(article_obj["geotags"])
        self.brandingImage = article_obj["brandingImage"]
        self.type = article_obj["type"]
        self.content = ""
        self.keywords = []

    def enrich_content(self, tg: TelegramService):
        self.content = fetch_content(self.details, tg)
        self.keywords = get_keywords(self.content)


class DBService:
    def __init__(self, uri: str):
        self.uri = uri
        self.client = pymongo.MongoClient(self.uri)
        self.articles = self.client.tagesschau.articles

    def push_article(self, article: Article):
        self.articles.insert_one(article.__dict__)

    def isExisting(self, article_id):
        article = self.articles.find_one({"id": article_id})
        return True if article else False

    def count_articles(self) -> int:
        return self.articles.count_documents({})

    def get_all_articles(self) -> Cursor:
        return self.articles.find({})

    def update_article(self, article_id: str, updated_fields: object):
        return self.articles.update_one({"_id": article_id}, {"$set": updated_fields})


def fetch_articles():
    res = requests.get(BASE_URL + NEWS_PATH + "?regions=13")
    if not res.ok:
        return []

    articles = res.json()["news"]
    return [Article(article) for article in articles]


def scrape(db: DBService, tg: TelegramService):

    articles = []
    try:
        articles = fetch_articles()
    except Exception as e:
        tg.send_msg("Error while fetching articles")
        tg.send_msg(str(e))
        print(e)

    exist_count = 0
    new_count = 0

    for article in articles:
        if not db.isExisting(article.id):
            print(f"fetching content: {article.title}")
            article.enrich_content(tg)  # fetch content
            db.push_article(article=article)
            new_count += 1
        else:
            print(f"already in DB: {article.title}")
            exist_count += 1

    msg = f"new entries: {new_count}, existing entries: {exist_count}"
    tg.send_msg(msg)
    print(msg)


def main():

    print("script startet")

    ENV = dotenv.dotenv_values()

    db = DBService(ENV["DB_URI"])
    tg = TelegramService(ENV["TELEGRAM_API_KEY"], ENV["CHAT_ID"])

    try:
        scrape(db, tg)
    except Exception as e:
        print(e)
        tg.send_msg("Error")
        tg.send_msg(str(e))


if __name__ == "__main__":
    main()
