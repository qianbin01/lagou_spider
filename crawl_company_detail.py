import requests
import pymongo
import config
from bs4 import BeautifulSoup
import time

client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate(config.MONGO_AUTH_NAME, config.MONGO_AUTH_PASSWORD)
company = db['company']
company_detail = db['company_detail']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Host': 'www.lagou.com'
}
base_url = 'https://www.lagou.com/gongsi/{}.html'
recruit_url = 'https://www.lagou.com/gongsi/searchPosition.json'
reply_url = 'https://www.lagou.com/gongsi/searchInterviewExperiences.json'
question_url = 'https://www.lagou.com/gongsi/q{}.html'


# 获取代理
def get_proxy():
    return requests.get("http://{}:5010/get/".format(config.MONGO_HOST)).content  # ip替换成自己的服务器地址


# 删除服务器无用代理
def delete_proxy(proxy):
    requests.get("http://{}:5010/delete/?proxy={}".format(config.MONGO_HOST, proxy))  # ip替换成自己的服务器地址


def get_html(doc, cid):
    company_detail_one = company_detail.find_one({'companyId': cid})
    if company_detail_one:
        print(doc['companyShortName'] + '已经存在，直接跳过')
        return False
    url = base_url.format(cid)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    span = soup.find('span', class_='company_content')
    if not span:
        while True:
            proxy = str(get_proxy(), encoding='utf-8')
            proxies = {
                'http': 'http://{}'.format(proxy),
                'https': 'http://{}'.format(proxy),
            }  # 获取并设置代理
            try:
                r = requests.get(url, headers=headers, proxies=proxies)
                soup = BeautifulSoup(r.text, 'lxml')
                span = soup.find('span', class_='company_content')
                if span:
                    break
            except Exception as e:
                if 'HTTPSConnectionPool' in str(e):
                    print('这个代理不能用，我删了你 {}'.format(proxy))  # 代理本身不可用则删除该代理
                    delete_proxy(proxy)
    detail_doc = doc.copy()
    # 公司介绍
    detail_doc['companyIntroduce'] = span.text
    # 图片
    img_ul = soup.find('ul', class_='company_img')
    img_list = []
    if img_ul:
        for li in img_ul.find_all('li'):
            img_list.append({'src': li.get('data-item')})
    detail_doc['imgList'] = img_list
    # 地址
    address_ul = soup.find('ul', class_='con_mlist_ul')
    address_list = []
    if address_ul:
        for li in address_ul.find_all('li'):
            address_list.append({
                'bigAddress': li.find('p', class_='mlist_li_title').text.strip().replace('\n', '').replace(' ', ''),
                'smallAddress': li.find('p', class_='mlist_li_desc').text.strip()
            })
    detail_doc['addressList'] = address_list
    # 历史记载
    history_ul = soup.find('ul', class_='history_ul')
    history_list = []
    if history_ul:
        for li in history_ul.find_all('li'):
            history_list.append({
                'historyDate': li.find('div', class_='li_date').text.strip().replace('\n', '.'),
                'historyText': li.find('span', class_='desc_real_title').text.strip()
            })
    detail_doc['historyList'] = history_list

    # 问题记载
    question_r = requests.get(question_url.format(cid))
    question_soup = BeautifulSoup(question_r.text, 'lxml')
    question_ul = question_soup.find('ul', id='question-answer-list')
    question_list = []
    if question_ul:
        for li in question_ul.find_all('li'):
            try:
                question_list.append({
                    'itemTitle': li.find('h4', class_='item-title').text.strip().replace('\n', '.'),
                    'itemTime': li.find('span', class_='item-time').text.strip(),
                    'itemStatus': li.find('div', class_='item-status').text.strip(),
                })
            except Exception as e:
                print(e)
                continue
    detail_doc['questionList'] = question_list

    # 反馈记载
    reply_data = {
        'companyId': cid,
        'positionType': '',
        'pageNo': 1,
        'pageSize': 10
    }
    reply_header = headers
    reply_header['Referer'] = 'https://www.lagou.com/gongsi/interviewExperiences.html?companyId={}'.format(cid)
    try:
        reply_r = requests.post(reply_url, data=reply_data, headers=reply_header)
        reply_list = reply_r.json().get('content').get('data').get('page').get('result')
        detail_doc['replyList'] = reply_list
    except Exception as e:
        print(e)
        print('这里请求太快，代理不够用，等3分钟再请求吧')
        time.sleep(180)
        reply_r = requests.post(reply_url, data=reply_data, headers=reply_header)
        reply_list = reply_r.json().get('content').get('data').get('page').get('result')
        detail_doc['replyList'] = reply_list
    # 职位记载
    recruit_data = {
        'companyId': cid,
        'positionFirstType': '全部',
        'schoolJob': False,
        'pageNo': 1,
        'pageSize': 100
    }
    recruit_header = headers
    recruit_header['Referer'] = 'https://www.lagou.com/gongsi/j{}.html'.format(cid)
    try:
        recruit_r = requests.post(recruit_url, data=recruit_data, headers=recruit_header)
        recruit_list = recruit_r.json().get('content').get('data').get('page').get('result')
        detail_doc['recruitList'] = recruit_list
    except Exception as e:
        print(e)
        print('这里请求太快，代理不够用，等3分钟再请求吧')
        time.sleep(180)
        recruit_r = requests.post(recruit_url, data=recruit_data, headers=recruit_header)
        recruit_list = recruit_r.json().get('content').get('data').get('page').get('result')
        detail_doc['recruitList'] = recruit_list
    print(detail_doc)
    company_detail.insert(detail_doc)


def get_cid_from_db():
    companies = company.find(no_cursor_timeout=True)
    for item in companies:
        del item['_id']
        print(item['companyShortName'])
        get_html(item, item['companyId'])
    companies.close()


if __name__ == '__main__':
    get_cid_from_db()
