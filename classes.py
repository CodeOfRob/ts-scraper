from datetime import datetime
from telegram.telegram import TelegramService
from util import extract_tags, fetch_content

class Article:

    def __init__(self, article_obj: object):
        self.id             = article_obj["externalId"]
        self.title          = article_obj["title"]
        self.date           = datetime.fromisoformat(article_obj["date"])
        self.tracking       = article_obj["tracking"]
        self.tags           = extract_tags(article_obj["tags"])
        self.regionIds      = article_obj["regionIds"]
        self.details        = article_obj["details"]
        self.topline        = article_obj["topline"]
        self.geotags        = extract_tags(article_obj["geotags"])
        self.brandingImage  = article_obj["brandingImage"]
        self.type           = article_obj["type"]
        self.content        = ""

    def enrich_content(self, tg: TelegramService):
        self.content = fetch_content(self.details, tg)
