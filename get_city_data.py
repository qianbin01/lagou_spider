import requests

import pymongo
import config

#
client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
# db.authenticate(config.MONGO_AUTH_NAME, config.MONGO_AUTH_PASSWORD)
city_districts = db['city_districts']
district_areas = db['district_areas']

subways_lines = db['subways_lines']
line_stops = db['line_stops']


def get_subway_data():
    city_with_subway_url = 'http://map.baidu.com/?qt=subwayscity'
    subway_detail_url = 'http://map.baidu.com/?qt=bsi&c={}'
    r = requests.get(city_with_subway_url)
    for item in r.json().get('subways_city').get('cities'):
        if item['code'] < 10000:
            url = subway_detail_url.format(item['code'])
            r = requests.get(url)
            subways_line = {
                'cityName': item['cn_name'],
                'subWayList': []
            }
            for subway in r.json().get('content'):
                if subway['line_name'].split('(')[0] not in subways_line['subWayList']:
                    subways_line['subWayList'].append(subway['line_name'].split('(')[0])

                line = line_stops.find_one(
                    {
                        'cityName': item['cn_name'],
                        'lineName': subway['line_name'].split('(')[0]
                    })
                if not line:
                    line = {
                        'cityName': item['cn_name'],
                        'lineName': subway['line_name'].split('(')[0],
                        'stops': []
                    }
                    for stop in subway['stops']:
                        line['stops'].append(stop['name'])
                    line_stops.insert(line)
                else:
                    stops = line['stops']
                    for stop in subway['stops']:
                        if stop['name'] not in stops:
                            stops.append(stop['name'])
                    line_stops.update({'_id': line['_id']}, {'$set': {'stops': stops}})
            subway_line = subways_lines.find_one({
                'cityName': item['cn_name'],
            })
            if not subway_line:
                subways_lines.insert(subways_line)


def combine_data():
    import json
    with open('city_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        cities = data.get('data')
        for city in cities:
            for area in city['cities']:
                city_district = {
                    'cityName': area['name'],
                    'districts': []
                }
                for country in area.get('counties'):
                    city_district['districts'].append(country['name'])
                    district_area = {
                        'cityName': area['name'],
                        'districts': country['name'],
                        'areas': [],
                    }
                    for circle in country.get('circles'):
                        district_area['areas'].append(circle['name'])
                    area_collection = district_areas.find_one({
                        'cityName': district_area['cityName'],
                        'districts': district_area['districts'],
                    })
                    if not area_collection:
                        district_areas.insert(district_area)
                city_collection = city_districts.find_one({
                    'cityName': city_district['cityName'],
                })
                if not city_collection:
                    city_districts.insert(city_district)


if __name__ == '__main__':
    combine_data()
    get_subway_data()

