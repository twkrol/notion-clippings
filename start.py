# Copyright (c) 2020 Tomasz Król
#
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software 
# is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import time
import configparser
import logging
from notion.client import NotionClient
# from clippings import parser
import parser
import progress

appname = "Notion Clippings"
version = "1.0.1"

#Configuration load
config = configparser.ConfigParser()
config.read('config.ini')

#Set logging configuration
# logging.basicConfig(level=config.get('runtime','logging'))
log = logging.getLogger(appname)
log.setLevel(config.get('runtime','logging'))

#Set screen log handler
log.addHandler(logging.StreamHandler())

#Set file log handler
log.addHandler(logging.FileHandler(config.get('runtime','logfile'))) if config.get('runtime','logfile') else None

#Welcome message
print(f"\nWelcome to {appname} v{version}")

#Reading clippings file
clips=[]
clippings_file = config.get('kindle', 'clippings_file')

print(f"- loading clippings from {clippings_file}...", end='')
try:
    with open(clippings_file, 'r', encoding='utf-8-sig') as infile:
        clips = parser.parse_clippings(infile)
        print(f"[{len(clips)} loaded]")
except FileNotFoundError:
    print(f"File {clippings_file} not found! Exiting.")
    exit()


#Notion configuration read
notion_api_token = config.get('notion', 'api_token')
notion_collection_url = config.get('notion', 'collection_url')

#Connect to Notion api
print(f"- connecting to Notion API...", end='')
client = NotionClient(token_v2=notion_api_token)
print(f"[success]")

#Open given collection page
print(f"- opening page...", end='')
page = client.get_block(notion_collection_url)
print(f" {page.title} [success]")

#Verify page type, must be a collection, preferrably without filters
if page.type != 'collection_view_page':
    log.critical('ERROR: The given page must be a collection (database), not a simple page!\nExiting.')
    exit()

#Load collection from Notion
collection_view = client.get_collection_view(notion_collection_url)
print(f"- loading collection {collection_view.name}...", end='')

collectionSize = len(collection_view.default_query().execute())
print(f"[{collectionSize} items]")

#Test collection structure for required properties
required_columns = ['Status', 'Text', 'Title', 'Authors', 'Date', 'Location']
props = collection_view.collection.get_schema_properties()

found_columns = list(filter(lambda x: x['name'] in required_columns, props))
if len(found_columns) != len(required_columns):
    print(f"ERROR: Your collection must include columns: {', '.join(required_columns)}.\nExiting!")
    exit()

######### DATA PROCESSING STARTS HERE ############

#Method to test if clipping from Notion exists in the given collection read from file
#Return: it's position or -1 if not found
def clipExists(clips, row):
    for i, clip in enumerate(clips):
        #data matching that could be optimized, but it works quite fast anyway
        if str(clip.document.title) == str(row.Title) and str(clip.metadata.timestamp.replace(second=0)) == str(row.Date.start) and str(clip.metadata.location) == str(row.Location):
            return i
    return -1


#Development only: used to trim clippings size to a reasonable level for testing
# clips = clips[:90]

#Iterate Notion collection (rows)
print(f"Comparing items")
for i, row in enumerate(collection_view.collection.get_rows()):
    log.debug(f"  row: {row.Status} / {row.Title} / {row.Authors} / {row.Date.start if row.Date else ''} / {row.Location}")
    atPosition = clipExists(clips, row)
    if atPosition > -1:
        del clips[atPosition]
    progress.progress(i+1, collectionSize, status=' comparing items' if i < collectionSize-1 else ' done.         \n')

#Inform what we have found
if len(clips) > 0:
    print(f"Adding {len(clips)} new item(s) to table {page.title}")
    new_status = config.get('notion', 'new_status')
    for i, clip in enumerate(clips):
        row = collection_view.collection.add_row()
        row.Status = new_status
        row.Title = clip.document.title
        row.Authors = clip.document.authors
        row.Date = clip.metadata.timestamp
        row.Text = clip.content
        row.Location = str(clip.metadata.location)
        progress.progress(i+1, len(clips), status=' adding items' if i < len(clips)-1 else ' done.       \n')
else:
    print(f"No new items found")


print(f"Done.")