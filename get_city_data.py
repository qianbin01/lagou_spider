import requests
import pymongo
import config

client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate(config.MONGO_AUTH_NAME, config.MONGO_AUTH_PASSWORD)
city_data = db['city_data']
subways_data = db['subways_data']


def get_subway_data():
    city_with_subway_url = 'http://map.baidu.com/?qt=subwayscity'
    subway_detail_url = 'http://map.baidu.com/?qt=bsi&c={}'
    r = requests.get(city_with_subway_url)
    for item in r.json().get('subways_city').get('cities'):
        if item['code'] < 10000:
            url = subway_detail_url.format(item['code'])
            r = requests.get(url)
            doc = {
                'cityName': item['cn_name'],
                'subWayList': []
            }
            for subway in r.json().get('content'):
                subway_doc = {
                    'lineName': subway['line_name'].split('(')[0],
                    'stops': []
                }
                for stop in subway['stops']:
                    subway_doc['stops'].append(stop['name'])
                doc['subWayList'].append(subway_doc)
            print(doc)
            find_data = subways_data.find_one(
                {'cityName': doc.get('cityName')})
            if not find_data:  # 查重后插入数据库
                subways_data.insert(doc)


def combine_data():
    import json
    with open('city_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        cities = data.get('data')
        for city in cities:
            for area in city['cities']:
                print(area)
                find_data = city_data.find_one(
                    {'name': area.get('name')})
                if not find_data:  # 查重后插入数据库
                    city_data.insert(area)


if __name__ == '__main__':
    combine_data()
    get_subway_data()
