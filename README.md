# gis-berlin-rents

## About

This tool crawls information about rental apartments from [immobilienscout24.de](https://www.immobilienscout24.de/Suche/S-T/P-1/Wohnung-Miete/Berlin/Berlin). More specifically in the area of Berlin. The crawled results are stored in a CSV file at the `./out` dir. Following format is used:
 
    price in EUR | flat size in m^2 | number of rooms | address | WGS84 latitude | WGS84 longitude | UTM zone | UTM latitude band | UTM easting coord | UTM northing coord | date of crawling 

Apartments with incomplete or ambiguous addresses are omitted. Apartments with missing features or having price ranges instead of a fixed price are also omitted. 

Crawled results are always appended to the file. Based on the apartments' addresses, the coordinates are extracted in a separate step from the Google Maps API. Random delays in between 2 and 10 seconds are added in between each API call to prevent getting blocked.

## Requirements

- Python 3.5 or higher

## Setup your Python Environment

Make sure to have all required packages installed. You can install them via following command:

        pip install requirements.txt

The `requirements.txt` is located at the project's root.

## Configuration
 
The `settings.py` allows you to adjust following settings:

- USER_AGENT: The user agent string to be used for the web crawler.
- DOWNLOAD_DELAY = The delay in seconds in between crawling each page
- PAGE_START = The page number to start crawling at
- PAGE_END = The number of the last page to be crawled

The remaining variables should not be changed unless the crawler needs to be adapted to reflect changes of the website to be crawled.
