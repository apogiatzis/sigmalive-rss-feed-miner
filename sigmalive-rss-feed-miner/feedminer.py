# -*-coding: utf-8 -*-
import logging
import requests
import xmltodict
import time

from tinydb import TinyDB

RSS_FEED_URL = "http://www.sigmalive.com/rss"
logger = logging.getLogger(__name__)

def fetch_news(*,db_path):
    logger.info("Fetching news from sigmalive...")
    db = TinyDB(db_path)
    sigmalive_tbl = db.table('sigmalive')

    rss_content = requests.get(RSS_FEED_URL).text
    parsed_feed = xmltodict.parse(rss_content)
    print('[+] Found %d items in RSS feed.' % (len(parsed_feed['rss']['channel']['item'])))
    for item in parsed_feed['rss']['channel']['item']:
        db.insert(item)

def get_stored_news(*, db_path):
    return TinyDB(db_path).all()

if __name__=='__main__':
    fetch_news(db_path="news_{}.json".format(int(time.time())))
    # print("There are currently %d items in DB" % 
    #         len(get_stored_news(db_path="news.json")))