import os

import pandas as pd

import is24crawler.settings

column_names = ['price', 'area', 'rooms', 'address', 'latitude', 'longitude', 'zone', 'band', 'x', 'y', 'date']
df = pd.read_csv(is24crawler.settings.CSV_FILE_PATH, header = None, delimiter = "|")
df.columns = column_names

# specified format at task: rooms | price | area | address | year | UTM x-coord | UTM y-coord | price per square meter
rdf = pd.DataFrame([df.rooms, df.price, df.area, df.address, pd.to_datetime(df.date).dt.year, df.x, df.y,
                    df.price / df.area]).transpose()

filePath = os.path.join(is24crawler.settings.OUT_DIR, "apartments-reformatted.csv")
rdf.to_csv(filePath, sep = '\t', index = False, header = None)
