import requests
import pymongo

# 基本信息
client = pymongo.MongoClient(host='localhost', port=27017)
db = client['data_db']
topic_data = db['topic']
article_data = db['article']
headers = {
    "Referer": "https://www.lagou.com/jobs/list_",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"
}


# 获取话题数据
def get_topic_by_crawl():
    for i in range(1, 100):
        url = 'https://yanzhi.lagou.com/topic/getTopicList.json?categoryId=&pageNo={}&pageSize=20'.format(i)
        r = requests.get(url)
        try:
            save_to_db(r.json().get('content').get('data').get('topicPage'), 'topic')
            if not r.json().get('content').get('data').get('hasMoreTopic'):
                return False
        except Exception as e:
            print(e)


# 获取文章数据
def get_article_by_crawl():
    for item in topic_data.find():
        topic_id = item.get('id')
        article_base_url = 'https://yanzhi.lagou.com/topic/moreTopicNewsList.json?topicId={}&pageNo={}&pageSize=20'
        for i in range(1, 100):
            url = article_base_url.format(topic_id, i)
            r = requests.get(url)
            try:
                save_to_db(r.json().get('content').get('data').get('topicNewsList'), 'article')
                if not r.json().get('content').get('data').get('hasMore'):
                    return False
            except Exception as e:
                print(e)


# 存储数据
def save_to_db(content, now_type):
    if now_type == 'topic':
        data_list = content.get('result')
        for item in data_list:
            find_data = topic_data.find_one(
                {'id': item.get('id'), 'title': item.get('title')})
            if not find_data:  # 查重后插入数据库
                topic_data.insert(item)
    elif now_type == 'article':
        data_list = content
        for item in data_list:
            find_data = article_data.find_one(
                {'questionId': item.get('news').get('questionId'), 'time': item.get('news').get('time')})
            if not find_data:  # 查重后插入数据库
                article_data.insert(item)
            else:
                print(find_data)


if __name__ == '__main__':
    get_topic_by_crawl()
    get_article_by_crawl()
