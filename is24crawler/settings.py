import os

# crawling
BOT_NAME = 'immoscout24bot'
ITEM_PIPELINES = {'is24crawler.pipelines.CsvWriterPipeline': 300}
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
DOWNLOAD_DELAY = 3
NUM_PAGES = 180

# results
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
CSV_FILE_PATH = os.path.join(os.path.abspath(os.path.join(PROJECT_DIR, os.pardir)), "out/apartments.csv")

# parsing
NUM_CRITERIA = 3
CRITERIA_SELECTOR = '.grid-item.result-list-entry__data-container .grid-item.result-list-entry__primary-criterion ' \
                    'dd::text'
ADDRESS_SELECTOR = '.result-list-entry__map-link::text'
