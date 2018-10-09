# 全栈系列Vue版拉勾，客官们来瞧瞧
模拟拉勾app系列---python爬虫系列
### 前言
本项目是本人在闲暇时间编写的一个初级引导项目，麻雀虽小五脏俱全，所使用的东西绝大多数在开发中都能用得到，但难免会存在很多地方需要完善。

由于近期要备战法考，且工作繁忙，没有时间维护，还存在很多BUG或需要优化的地方，希望多多提出（有空了就改），当然能给个star什么的就更好了.

为了方便访问，也加入了mock数据,但不是很全，若需要完整体验，请按照下方步骤实现。

前端项目由Vue框架编写，其余部分涉及到node、python等可移至下方项目或自行查阅。
### 注意：本项目个人开发练习，不作为任何商业用途

# todolist
+ ~~职位数据爬取~~  √
+ ~~公司数据爬取~~  √
+ ~~评论数据爬取~~  √
+ ~~用户数据爬取~~  √
+ ~~文章数据爬取~~  √
+ ~~话题数据爬取~~  √
+ ~~城市及地铁数据爬取~~  √
+ ~~数据格式化及相应处理~~  √

# 技术栈
前端：
+ vue全家桶
+ es6
+ scss
+ mint-ui
+ mockjs
+ jquery

转发服务器：
+ node
+ express

实际api服务器:
+ python3
+ mongodb

爬虫：
+ python3

# 效果演示
### 首次载入
![](screenshots/loading.gif)
### 登录注册
![](screenshots/login.gif)
### 首页
![](screenshots/home.gif)
### 文章阅读
![](screenshots/read.gif)
### 选择城市
![](screenshots/choose_city.gif)
### 职位查看
![](screenshots/recruit.gif)
### 筛选
![](screenshots/recurit_want.gif)
### 排序
![](screenshots/sort.gif)
### 排序2
![](screenshots/sort_2.gif)
### 简历修改
![](screenshots/edit_resume.gif)
### 我的设置
![](screenshots/setting.gif)

ps:还有更多的设置就不截图了，有点大，有兴趣的clone下去看看吧

# 线上地址

# 说明
前端地址:https://github.com/qianbin01/lagou_vue

代理api地址:https://github.com/qianbin01/lagou_node

api地址:https://github.com/qianbin01/lagou_python_api

爬虫地址:https://github.com/qianbin01/lagou_spider
# 项目配置
ubuntu 16.04
# 运行步骤
  必备步骤：
  1. 运行爬虫项目
  2. 运行python-api项目
  3. 运行node-api转发项目
  4. 运行本项目
  
  本项目步骤：
  
  1. git clone https://github.com/qianbin01/lagou_spider.git
  2. cd lagou_spider
  3. pip install -r requirements.txt
  4. 搭建mongodb服务
  5. 修改代理服务器ip，如何自搭代理服务器戳
<a href="https://github.com/jhao104/proxy_pool">这里</a>
  6. 根据不同系统设置定时任务
#### windows
    schtasks语法：schtasks /create /tn 设定定时运行的名字 /tr “运行程序” /sc daily /st时间
    demo:
    schtasks /create /tn 定时运行 /tr "notepad" /sc daily /st 12:30（12:30时运行记事本）
#### linux(ubuntu,mac)
    crontab –e 设置
    crontab –l 查看
    cmd:
    分 时 天  周 月  命令（*代表当前单位的所有时间）
    *  *  *  *  *  command
    每天9点运行一次语句为：
    0  9  *  *  *  /usr/bin/python3 /home/qb/do_something.py
  
# 其他
 1. 测试地址: http://114.67.151.31:5010 (单机勿压。感谢)
 2. ps:拉勾头条的地址找不到，暂用36kr代替
    
 
# 点点你们的小手吧
知乎专栏：https://zhuanlan.zhihu.com/c_1010582778160779264

掘金:https://juejin.im/user/5b8291bce51d4538ab043911

思否:https://segmentfault.com/u/qishidexinxin

希望对大家有帮助

![](http://oh343spqg.bkt.clouddn.com/dianzan.jpg)

大佬们赞助一波续费服务器吧

<img src="http://oh343spqg.bkt.clouddn.com/zhifubao.jpg" width="150" hegiht="50" />


<img src="http://oh343spqg.bkt.clouddn.com/%E5%BE%AE%E4%BF%A1.jpg" width="150" hegiht="50" />

# License
    MIT

