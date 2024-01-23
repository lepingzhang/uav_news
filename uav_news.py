import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from plugins import register, Plugin, Event, logger, Reply, ReplyType

@register
class UAVNews(Plugin):
    name = "uav_news"
    command = "#获取新闻"

    def __init__(self):
        super().__init__()
        self.target_date = datetime.now().strftime('%Y-%m-%d')

    def get_news(self):
        url = 'https://www.youuav.com/news/search.php'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            response = requests.get(url, headers=headers)
            news_data = []

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                news_items = soup.find_all('li', class_='indent')
                for item in news_items:
                    news_date_div = item.find('div', class_='time')
                    if news_date_div:
                        news_date = news_date_div.get_text().strip()
                        if news_date.startswith(self.target_date):
                            news_link = item.find('a')['href']
                            news_title = item.find('a')['title']
                            news_data.append(f'标题: {news_title}\n链接: {news_link}\n')
                        else:
                            break
            return news_data

        except requests.RequestException as e:
            return [f'请求过程中发生错误：{e}']

    def process_message(self, message):
        if message == self.command:
            news_data = self.get_news()
            return '\n'.join(news_data) if news_data else '抱歉，今天没有找到新闻。'
        else:
            return f'请输入"{self.command}"来获取今日新闻内容。'

    # 添加缺失的抽象方法
    def did_receive_message(self, message, room):
        # 在这里处理接收到的消息
        pass

    def help(self):
        # 返回一个字符串，描述这个插件的功能和如何使用
        return "输入 '#获取新闻' 以获取最新的新闻。"

    def will_decorate_reply(self, reply, message, room):
        # 在这里处理回复修饰
        return reply

    def will_generate_reply(self, message, room):
        # 在这里处理回复生成
        return True

    def will_send_reply(self, reply, message, room):
        # 在这里处理回复发送前的逻辑
        pass
