# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SuningscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    shopname = scrapy.Field()
    url = scrapy.Field()
    crawldate = scrapy.Field()

class CommentsItem(scrapy.Item):
    url = scrapy.Field()
    commentstext = scrapy.Field()