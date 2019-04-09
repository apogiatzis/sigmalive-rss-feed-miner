# -*-coding: utf-8 -*-
import logging
import requests
import xmltodict


from timeloop import Timeloop
from datetime import timedelta
from tinydb import TinyDB, Query

RSS_FEED_URL = "http://www.sigmalive.com/rss"
tl = Timeloop()
logger = logging.getLogger(__name__)

def fetch_news(*,db_path):
    logger.info("Fetching news from sigmalive...")
    db = TinyDB(db_path)
    sigmalive_tbl = db.table('sigmalive')

    rss_content = requests.get(RSS_FEED_URL).text
    parsed_feed = xmltodict.parse(rss_content)
    # print('[+] Found %d items in RSS feed.' % (len(parsed_feed['rss']['channel']['item'])))
    news_item = Query()
    for item in parsed_feed['rss']['channel']['item']:
        if len(db.search(news_item.id == item['id'])) == 0:
            db.insert(item)

def fetch_news_periodically(*,db_path, interval):
    tl.job(fetch_news(db_path=db_path))
    tl.start(block=True)

def get_stored_news(*, db_path):
    return TinyDB(db_path).all()

if __name__=='__main__':
    fetch_news_periodically(db_path="db.json", interval=10)
    print(get_stored_news(db_path="db.json"))