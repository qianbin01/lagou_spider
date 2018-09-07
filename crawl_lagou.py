import requests
import pymongo
import config

# 基本信息
client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate(config.MONGO_AUTH_NAME, config.MONGO_AUTH_PASSWORD)
recruit_data = db['recruit']
topic_data = db['topic']
company_data = db['company']
article_data = db['article']
headers = {
    "Referer": "https://www.lagou.com/jobs/list_",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
}
keywords = [
    'java后端',
    'java',
    'java web',
    'java 实习',
    'java 分布式',
    '前端',
    '前端实习',
    'javascript',
    'web',
    'vue',
    'html5',
    '全栈',
    'node',
    'node.js',
    'web实习',
    'react',
    'angular',
    'reactnative',
    'python',
    'python爬虫',
    '大数据',
    'django',
    'flask',
    'python实习',
    '量化交易',
    'mongodb',
    'redis',
    '机器学习',
    '算法',
    '计算机视觉',
    '人工智能',
    '自然语言',
    '程序员',
    '设计师',
    'ui',
    '产品经理',
    '运维',
    '运营',
    '互联网运营'
]


# 获取代理
def get_proxy():
    return requests.get("http://{}:5010/get/".format(config.MONGO_HOST)).content  # ip替换成自己的服务器地址


# 删除服务器无用代理
def delete_proxy(proxy):
    requests.get("http://{}:5010/delete/?proxy={}".format(config.MONGO_HOST, proxy))  # ip替换成自己的服务器地址


# 获取求职岗位数据
def get_data_by_crawl(city, kw):
    url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&city={}'.format(city)
    proxy = str(get_proxy(), encoding='utf-8')
    proxies = {
        'http': 'http://{}'.format(proxy),
        'https': 'http://{}'.format(proxy),
    }  # 获取并设置代理
    for i in range(1, 100):
        data = {"first": "true", "pn": i, "kd": kw}
        base_request = requests.post(url, data=data, headers=headers, timeout=3)
        try:
            base_request.json().get('content')
        except Exception as e:
            print(e)
            continue
        if not base_request.json().get('content', ''):
            flag = False
            while not flag:  # 若代理ip没走通则换一个
                try:
                    r = requests.post(url, data=data, headers=headers, timeout=3, proxies=proxies)
                    if not r.json().get('content', ''):
                        raise Exception('这个ip不能用')
                    save_to_db(r.json().get('content', ''), 'data')  # 存入数据库
                    flag = True  # 成功获取数据跳出循环
                except Exception as e:
                    if 'HTTPSConnectionPool' in str(e):
                        print('这个代理不能用，我删了你 {}'.format(proxy))  # 代理本身不可用则删除该代理
                        delete_proxy(proxy)
                    proxy = str(get_proxy(), encoding='utf-8')
                    proxies = {
                        'http': 'http://{}'.format(proxy),
                        'https': 'http://{}'.format(proxy),
                    }  # 切换代理
        else:
            save_to_db(base_request.json().get('content', ''), 'data')  # 存入数据库


# 获取公司数据
def get_company_by_crawl():
    headers['Referer'] = 'https://www.lagou.com/gongsi/0-0-0-0'
    url = 'https://www.lagou.com/gongsi/0-0-0-0.json'
    proxy = str(get_proxy(), encoding='utf-8')
    proxies = {
        'http': 'http://{}'.format(proxy),
        'https': 'http://{}'.format(proxy),
    }  # 获取并设置代理
    for i in range(1, 100):
        data = {
            'first': False,
            'pn': i,
            'sortField': 1,
            'havemark': 0
        }
        print(i)
        base_request = requests.post(url, data=data, headers=headers, timeout=3)
        if '网络出错啦' in base_request.text or not base_request.json().get('result', ''):
            flag = False
            while not flag:  # 若代理ip没走通则换一个
                try:
                    r = requests.post(url, data=data, headers=headers, timeout=3, proxies=proxies)
                    if not r.json().get('result', ''):
                        if not r.json().get('totalCount'):
                            raise Exception('这个ip不能用')
                        else:
                            return False
                    save_to_db(r.json().get('result', ''), 'company')  # 存入数据库
                    flag = True  # 成功获取数据跳出循环
                except Exception as e:
                    if 'HTTPSConnectionPool' in str(e):
                        print('这个代理不能用，我删了你 {}'.format(proxy))  # 代理本身不可用则删除该代理
                        delete_proxy(proxy)
                    proxy = str(get_proxy(), encoding='utf-8')
                    proxies = {
                        'http': 'http://{}'.format(proxy),
                        'https': 'http://{}'.format(proxy),
                    }  # 切换代理
        else:
            save_to_db(base_request.json().get('result', ''), 'company')  # 存入数据库


# 存储数据
def save_to_db(content, now_type):
    if now_type == 'company':
        data_list = content
        for item in data_list:
            print(item)
            find_data = company_data.find_one(
                {'companyId': item.get('companyId')})
            if not find_data:  # 查重后插入数据库
                company_data.insert(item)
    elif now_type == 'data':
        data_list = content.get('positionResult').get('result')
        for item in data_list:
            find_data = recruit_data.find_one(
                {'companyId': item.get('companyId'), 'createTime': item.get('createTime')})
            if not find_data:  # 查重后插入数据库
                print(item)
                recruit_data.insert(item)


def format_img():
    recruits = recruit_data.find(no_cursor_timeout=True)
    for recruit in recruits:
        try:
            company_logo = recruit['companyLogo']
            if 'http://www.lgstatic.com' not in company_logo and 'https://static.lagou' not in company_logo:
                company_logo = 'http://www.lgstatic.com/' + company_logo
                recruit_data.update({'_id': recruit['_id']}, {'$set': {'companyLogo': company_logo}})
        except Exception as e:
            print(e)
            continue
    recruits.close()
    companies = company_data.find(no_cursor_timeout=True)
    for company in companies:
        try:
            company_logo2 = company['companyLogo']
            if 'http://www.lgstatic.com' not in company_logo2 and 'https://static.lagou' not in company_logo2:
                company_logo2 = 'http://www.lgstatic.com/' + company_logo2
                recruit_data.update({'_id': company['_id']}, {'$set': {'companyLogo': company_logo2}})
        except Exception as e:
            print(e)
            continue
    companies.close()


if __name__ == '__main__':
    get_company_by_crawl()
    for keyword in keywords:
        get_data_by_crawl('全国', keyword)
    format_img()
