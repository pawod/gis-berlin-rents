import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import csv
import datetime


class Is24Crawler(scrapy.Spider):
    name = "appartments"
    feature_selector = '.grid-item.result-list-entry__data-container .grid-item.result-list-entry__primary-criterion dd::text'
    address_selector = '.result-list-entry__map-link::text'
    num_features = 3;

    def start_requests(self):
        for i in range(1, 3):
            url = 'https://www.immobilienscout24.de/Suche/S-T/P-{0}/Wohnung-Miete/Berlin/Berlin'.format(i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        raw_features = list(map(str.strip, response.css(Is24Crawler.feature_selector).extract()))
        filtered_features = Is24Crawler.filter_features(raw_features)
        if len(filtered_features) % Is24Crawler.num_features != 0:
            raise AssertionError(
                "Number of features is not divisible by 3: Extracted features are not uniquely assignable to an item.")
        addresses = list(map(str.strip, response.css(Is24Crawler.address_selector).extract()))
        coords = Is24Crawler.get_coordinates(addresses)

        # todo: write csv
        strings = response.url.split("/")
        page = strings[5][2:]
        queryname = "{0}-{1}-{2}".format(strings[6], strings[7], strings[8])
        filename = "{0}-{1}.csv".format(queryname, page)

        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            for i in range(len(filtered_features)):
                if not coords or len(coords[i]) != 2:
                    print("skipping address: '{}'".format(addresses[i]))
                    continue
                feature_set = filtered_features[3 * i:3 * i + 3:1]
                price = feature_set[0].split()[0].replace('.', '')
                size = feature_set[1].split()[0].replace(',', '.')
                rooms = feature_set[2]
                lat = coords[i][0]
                lng = coords[i][1]

                row = [price, size, rooms, addresses[i], str(lat), str(lng),
                       datetime.datetime.now().strftime("%Y-%m-%d")]
                writer.writerow(row)

    @staticmethod
    def filter_features(raw_features):
        return list(filter(lambda x: len(x) > 0 and 'nach Vereinbarung' not in x and '-' not in x, raw_features))

    @staticmethod
    def get_coordinates(addresses):
        coords = []
        for addr in addresses:
            parts = addr.split(",")
            if len(parts) != 3:
                coords.append("INVALID: incomplete address")
                continue

            street = parts[0]
            district = parts[1].strip().split()
            district_1 = district[0]
            district_2 = district[1][1:-1]
            city = parts[2].strip()

            request = 'http://maps.google.com/maps/api/geocode/json?address={},+{},+{},+{}'.format(street,
                                                                                                   district_1,
                                                                                                   district_2,
                                                                                                   city)

            r = requests.get(request)
            results = r.json()["results"]
            if len(results) > 1:
                coords.append("INVALID: ambiguous address")
            else:
                location = results[0]["geometry"]["location"]
                coords.append([location["lat"], location["lng"]])
        return coords


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(Is24Crawler)
process.start()  # the script will block here until the crawling is finished
