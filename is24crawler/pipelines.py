import csv

from is24crawler import settings


class CsvWriterPipeline(object):
    def __init__(self):
        self.file = None

    def open_spider(self, spider):
        self.file = open(settings.CSV_FILE_PATH, 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        """
        writes a csv file for each crawled page.
        format: price in eur|size in m^2|number of rooms|address|latitude\longitude\date.
        """
        writer = csv.writer(self.file, delimiter = '|')
        for apartment in item["apartments"]:
            row = [apartment["price"], apartment["size"], apartment["rooms"], apartment["address"], apartment["lat"],
                   apartment["lng"], apartment["date"]]
            writer.writerow(row)
            self.file.flush()
        print("page {} processed.".format(item["page"]))
        return item
