import requests, zipfile
import io
import json
import os
import csv

from progress.bar import Bar
from utils import *

config_exists()
from config import *

class NewsItem(object):
    def __init__(self, data):
        self.data = data
        self.id = int(data['id'])
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, NewsItem) and self.id == other.id

    def __repr__(self):
        return "NewsItem:{0}".format(self.id)

def get_finished_jobs():
    all_jobs = []
    jobs_in_page = []
    page = 1
    while True:
        url = (CONFIG.GITLAB_URL+"projects/{0}/jobs?scope[]=success&page={1}").format(CONFIG.PROJECT_ID, page)
        r = requests.get(url, headers={"PRIVATE-TOKEN":CONFIG.API_KEY}) 
        jobs_in_page = json.loads(r.content)
        if len(jobs_in_page) == 0: break
        all_jobs.extend(jobs_in_page)
        page += 1
    return  all_jobs

def download_artifact(job_id, extract_dir):
    url = (CONFIG.GITLAB_URL+"projects/{0}/jobs/{1}/artifacts").format(CONFIG.PROJECT_ID, job_id)
    r = requests.get(url, headers={"PRIVATE-TOKEN":CONFIG.API_KEY}, stream=True)
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
        z.extractall(extract_dir)
    except Exception as e:
        ## Just in case artifacts 
        pass


def download_all_artifacts(extract_id):
    jobs = get_finished_jobs()
    bar = Bar('Downloading artifacts', max=len(jobs))
    for j in jobs:
        download_artifact(j['id'], CONFIG.EXTRACT_DIR)
        bar.next()
    bar.finish()

def read_all_artifacts(extract_dir):
    all_news = set()
    for file in os.listdir(extract_dir):
        full_filename = "%s/%s" % (extract_dir, file)
        with open(full_filename,'r') as fi:
            artifact_news = json.load(fi)
            for n in artifact_news['_default'].values():
                all_news.add(NewsItem(n))
    return all_news

def write_to_csv(news_set, csv_path):
    with open(csv_path, 'w') as csv_file:
        columns = ['id', 'category', 'title', 'link', 'description','pubDate','live','image','image_length','image_type']
        writer = csv.writer(csv_file)
        writer.writerow(columns)
        bar = Bar('Saving news to csv', max=len(news_set))
        for news_item in news_set:
            try:
                row =  [news_item.data['id'], news_item.data['category'], news_item.data['title'],
                        news_item.data['link'], news_item.data['description'], news_item.data['pubDate'],
                        news_item.data['live'], news_item.data['enclosure']['@url'], news_item.data['enclosure']['@length'],
                        news_item.data['enclosure']['@type']]
                writer.writerow(row)
            except Exception as e:
                print('An exception occured while processing news item:', e)
                print('News Item: ', news_item.data)
            bar.next()
        bar.finish()
            
check_config_values(CONFIG)
download_all_artifacts(CONFIG.EXTRACT_DIR)
news_set = read_all_artifacts(CONFIG.EXTRACT_DIR)

print('[+] Number of news mined: {}'.format(len(news_set)))
write_to_csv = write_to_csv(news_set, "sigmalive_news.csv")