# __init__.py
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from .plugin import Plugin, register

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
