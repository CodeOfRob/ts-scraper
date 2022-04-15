import time
import requests
import constants
import dotenv
from classes import Article
from db.db import DBService
from telegram.telegram import TelegramService


def fetch_articles():

    res = requests.get(constants.BASE_URL + constants.NEWS_PATH + "?regions=13")

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
            article.enrich_content(tg) # fetch content
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

    while True: 
        try:
            scrape(db, tg)
        except Exception as e:
            print(e)
            tg.send_msg("Error")
            tg.send_msg(str(e))
        time.sleep(int(ENV["REQ_DELAY"]))

    # print(db.count_articles())
   

if __name__ == "__main__":
    main()