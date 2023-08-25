# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter.adapter import ItemAdapter
import config
from pymongo import MongoClient


class BookscraperPipeline:

    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        # changing price, price_exc_tax, price_inc_tax and tax to float from string

        price_keys = ["price", "price_exc_tax", "price_inc_tax", "tax"]
        for price_key in price_keys:
            value = adapter.get(price_key).replace("£", "")
            adapter[price_key] = float(value)

        # changing product_type and category to lowercase

        lowercase_keys = ["product_type", "category"]
        for key in lowercase_keys:
            adapter[key] = adapter.get(key).lower()

        # changing reviews to integer

        adapter["reviews"] = int(adapter.get("reviews"))

        # changing the rating field

        star_rating = adapter.get("rating")
        star_rating = star_rating.split(" ")[1].lower()
        if star_rating == "one":
            adapter["rating"] = 1
        elif star_rating == "two":
            adapter["rating"] = 2
        elif star_rating == "three":
            adapter["rating"] = 3
        elif star_rating == "four":
            adapter["rating"] = 4
        elif star_rating == "five":
            adapter["rating"] = 5

        # changing availability to int from str

        available_books = adapter.get("availability")
        available_books = available_books.split("(")[1][:2].strip()
        adapter["availability"] = int(available_books)

        return item

class SaveToDatabase:

    def __init__(self):
        self.mongo_uri = config.mongo_uri

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        db = self.client.scrapy
        self.collection = db.books

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item
    
    def close_spider(self, spider):
        self.client.close()
        