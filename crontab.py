import dotenv
from app import scrape

from db.db import DBService
from telegram.telegram import TelegramService

def main():
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