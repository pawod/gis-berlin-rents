import scrapy


class ResultPage(scrapy.Item):
    apartments = scrapy.Field()
    page = scrapy.Field()
