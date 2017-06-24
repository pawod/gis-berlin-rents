import datetime
import os
import random
from pprint import pprint
from time import sleep

import requests
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from is24crawler import settings
from is24crawler.apartment import Apartment
from is24crawler.resultpage import ResultPage


class Immoscout24Bot(scrapy.Spider):
    name = "immoscout24bot"

    def start_requests(self):
        for i in range(1, settings.NUM_PAGES + 1):
            url = 'https://www.immobilienscout24.de/Suche/S-T/P-{0}/Wohnung-Miete/Berlin/Berlin'.format(i)
            yield scrapy.Request(url = url, callback = self.parse)

    def parse(self, response):
        criteria = list(
            filter(lambda x: len(x) > 0, (map(str.strip, response.css(settings.CRITERIA_SELECTOR).extract()))))
        if len(criteria) % settings.NUM_CRITERIA != 0:
            raise AssertionError(
                "Number of extracted criteria is not divisible by {}: Extracted criteria are not uniquely assignable "
                "to an apartment.".format(settings.NUM_CRITERIA))

        addresses = list(map(str.strip, response.css(settings.ADDRESS_SELECTOR).extract()))
        if len(addresses) != len(criteria) / settings.NUM_CRITERIA:
            raise AssertionError(
                "Number of extracted criteria sets ({}) does not match number of extracted addresses ({})".format(
                    len(criteria), len(addresses)))

        coordinates = Immoscout24Bot.get_coordinates(addresses)
        apartments = Immoscout24Bot.parse_features(criteria, coordinates, addresses)
        page = response.url.split("/")[5][2:]
        yield ResultPage(apartments = apartments, page = page)

    @staticmethod
    def parse_features(criteria, coordinates, addresses):
        """
        parses all features of an apartment.
        :param criteria: a list of parsed feature sets for each crawled apartment.
        :param coordinates: tuples (lat,lng) for each crawled apartment.
        :param addresses: the addresses for each crawled apartment.
        :return: a list of feature sets.
        """
        parsed = []
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        for i in range(len(coordinates)):
            if len(coordinates[i]) != 2:
                print("skipping invalid address: '{}'".format(addresses[i]))
                continue

            criteria_set = criteria[settings.NUM_CRITERIA * i:settings.NUM_CRITERIA * i + settings.NUM_CRITERIA:1]
            if any('nach Vereinbarung' in x or '-' in x for x in criteria_set):
                print("skipping invalid criteria set:")
                pprint(criteria_set)
                continue

            price = criteria_set[0].split()[0].replace('.', '')
            size = criteria_set[1].split()[0].replace(',', '.')
            rooms = criteria_set[2]
            lat = coordinates[i][0]
            lng = coordinates[i][1]

            apartment = Apartment(price = price, size = size, rooms = rooms, address = addresses[i], lat = lat,
                                  lng = lng, date = date)
            parsed.append(apartment)
        return parsed

    @staticmethod
    def get_coordinates(addresses):
        """
        gets the longitude and latitude for a given address from the google API.
        :param addresses: a list of addresses.
        :return: a list of tuples (lat,lng).
        """
        coords = []
        for idx, addr in enumerate(addresses):
            parts = addr.split(",")
            if len(parts) != 3:
                coords.append("incomplete address")
                continue

            street = parts[0]
            area = parts[1].replace(")", "").split('(')
            district = area[0].strip()
            subdistrict = area[1]
            city = parts[2].strip()

            if district != subdistrict:  # duplicate params result in ambiguous results
                request = 'http://maps.google.com/maps/api/geocode/json?address={},+{},+{},+{}'.format(street, district,
                                                                                                       subdistrict,
                                                                                                       city)
            else:
                request = 'http://maps.google.com/maps/api/geocode/json?address={},+{},+{}'.format(street, district,
                                                                                                   city)

            if idx > 0:
                sleep(random.randint(2, 10))  # prevent getting blocked from the google API

            r = requests.get(request)
            results = r.json()["results"]
            result_types = list(map(lambda x: ",".join(x["types"]), results))
            exact_matches_idx = [index for index, value in enumerate(result_types) if
                                 "street_address" in value or "establishment" in value or "premise" in value]

            if len(exact_matches_idx) != 1:
                coords.append("ambiguous address")
            else:
                idx = exact_matches_idx[0]
                location = results[idx]["geometry"]["location"]
                coords.append([location["lat"], location["lng"]])
        return coords


os.environ["SCRAPY_SETTINGS_MODULE"] = "is24crawler.settings"
process = CrawlerProcess(get_project_settings())
process.crawl(Immoscout24Bot)
process.start()
