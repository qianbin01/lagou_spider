import requests
import pymongo
import config

client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate(config.MONGO_AUTH_NAME, config.MONGO_AUTH_PASSWORD)
news = db['news_36kr']


def get_news_by_36kr():
    list_base_url = 'https://36kr.com/api/search-column/218?per_page=100&page={}'
    detail_base_url = 'https://36kr.com/api/post/{}'
    for i in range(1, 2):
        url = list_base_url.format(i)
        r = requests.get(url)
        for item in r.json().get('data').get('items'):
            detail_url = detail_base_url.format(item['id'])
            detail_r = requests.get(detail_url)
            detail_data = detail_r.json().get('data')
            single_data = {
                'nid': item['id'],
                'summary': item['summary'],
                'title': item['title'],
                'publish_item': detail_data['published_at'],
                'extraction_tags': item['extraction_tags'],
                'cover': item['cover'],
                'content': detail_data['content'],
                'count': detail_data.get('counters').get('view_count')
            }
            insert_data = news.find_one({'nid': item['id']})
            if not insert_data:
                print(single_data)
                news.insert(single_data)


def format_news():
    import re
    p = re.compile('\"(.*?)\"')
    for item in news.find():
        if type(item['extraction_tags']) == str:
            match = p.findall(item['extraction_tags'])
            news.update({'_id': item['_id']}, {'$set': {'extraction_tags': match}})
            print(match)


if __name__ == '__main__':
    get_news_by_36kr()
    format_news()
