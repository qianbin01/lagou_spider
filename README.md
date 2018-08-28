# lagou_spider
模拟拉勾app系列---数据准备爬虫

1.安装依赖包 pip install -r requirements.txt

2.搭建mongodb服务

3.修改代理服务器ip，如何自搭代理服务器戳
<a href="https://github.com/jhao104/proxy_pool">这里</a>


4.根据不同系统设置定时任务
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

测试地址: http://114.67.151.31:5010 (单机勿压。感谢)

ps:拉钩头条的地址找不到，暂用36kr代替
