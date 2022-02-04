import pymongo
from classes import Article


class DBService:

    def __init__(self, uri: str):
        self.uri = uri
        self.client = pymongo.MongoClient(self.uri)
        self.articles = self.client.tagesschau.articles

    def push_article(self, article: Article):
        self.articles.insert_one(article.__dict__)

    def isExisting(self, article_id):
        article = self.articles.find_one({"id":article_id})
        return True if article else False