import requests

city_with_subway_url = 'http://map.baidu.com/?qt=subwayscity'
subway_detail_url = 'http://map.baidu.com/?qt=bsi&c={}'
r = requests.get(city_with_subway_url)
data_list = []
subway_names = []
for item in r.json().get('subways_city').get('cities'):
    if item['code'] < 10000:
        url = subway_detail_url.format(item['code'])
        r = requests.get(url)
        doc = {
            'cityName': item['cn_name'],
            'subWayList': []
        }
        for subway in r.json().get('content'):
            if subway['line_name'].split('(')[0] not in subway_names:
                subway_names.append(subway['line_name'].split('(')[0])
            subway_doc = {
                'lineName': subway['line_name'].split('(')[0],
                'stops': []
            }
            for stop in subway['stops']:
                subway_doc['stops'].append(stop['name'])
            doc['subWayList'].append(subway_doc)
        subway_names = []
        data_list.append(doc)
print(data_list)
