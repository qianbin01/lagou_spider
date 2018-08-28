import requests
import pymongo
import config

# 基本信息
client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate(config.MONGO_AUTH_NAME, config.MONGO_AUTH_PASSWORD)
topic_data = db['topic']
article_data = db['article']
comment_data = db['comment']
comment_user = db['comment_user']
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
            save_to_db(r.json().get('content').get('data').get('topicPage'), 'topic', '')
            if not r.json().get('content').get('data').get('hasMoreTopic'):
                return False
        except Exception as e:
            print(e)


# 获取文章数据
def get_article_by_crawl():
    topics = topic_data.find(no_cursor_timeout=True)
    for item in topics:
        topic_id = item.get('id')
        article_base_url = 'https://yanzhi.lagou.com/topic/moreTopicNewsList.json?topicId={}&pageNo={}&pageSize=20'
        for i in range(1, 100):
            url = article_base_url.format(topic_id, i)
            print(url)
            r = requests.get(url)
            try:
                save_to_db(r.json().get('content').get('data').get('topicNewsList'), 'article', topic_id)
                if not r.json().get('content').get('data').get('hasMore'):
                    break
            except Exception as e:
                print(e)
                if r.json():
                    if r.json().get('content'):
                        if r.json().get('content').get('data'):
                            if not r.json().get('content').get('data').get('hasMore'):
                                break
                        else:
                            break
                    else:
                        break
                else:
                    break
    topics.close()


# 存储数据
def save_to_db(content, now_type, topic_id):
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
                item['topic_id'] = topic_id
                item['questionId'] = str(item.get('news').get('questionId'))
                item['time'] = item.get('news').get('time')
                item['news']['topic_id'] = topic_id
                article_data.insert(item)


# 将评论单独划出
def get_comment_from_article():
    articles = article_data.find(no_cursor_timeout=True)
    for item in articles:
        comment_list = item.get('news').get('answerInfoList')
        if comment_list:
            for sub_item in comment_list:
                comment_item = comment_data.find_one({'answerId': sub_item.get('answerId')})
                if not comment_item:
                    sub_item['article_id'] = str(item['questionId'])
                    comment_data.insert(sub_item)
        article_data.update({'_id': item['_id']}, {'$set': {'answerInfoList': []}})


# 将评论用户从评论中单独划出
def get_user_from_comment():
    comments = comment_data.find(no_cursor_timeout=True)
    for item in comments:
        sub_item = item.get('answerUser')
        comment_user_item = comment_user.find_one({'id': sub_item.get('id')})
        if not comment_user_item:
            sub_item['answerId'] = item['answerId']
            comment_user.insert(sub_item)
        comment_data.update({'_id': item['_id']}, {'$set': {'answerUser': ''}})


if __name__ == '__main__':
    get_topic_by_crawl()
    get_article_by_crawl()
    get_comment_from_article()
    get_user_from_comment()
