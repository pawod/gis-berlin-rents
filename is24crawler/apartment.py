import scrapy


class Apartment(scrapy.Item):
    price = scrapy.Field()
    size = scrapy.Field()
    rooms = scrapy.Field()
    address = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()
    date = scrapy.Field()
