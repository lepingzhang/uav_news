import requests
from bs4 import BeautifulSoup
from datetime import datetime
from plugins import register, Plugin, Event, Reply, ReplyType
from utils.api import send_txt  # 确保这个导入语句是正确的

@register
class UAVNews(Plugin):
    name = 'uav_news'
    def __init__(self, config=None):
        super().__init__(config=config)
        self.target_date = datetime.now().strftime('%Y-%m-%d')
        self.commands = self.config.get('command', [])

    def get_news(self):
        url = 'https://www.youuav.com/news/search.php'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        news_data = []

        try:
            response = requests.get(url, headers=headers)
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
        except Exception as e:
            news_data.append('抱歉，无法获取无人机新闻。')
        
        return news_data

    def did_receive_message(self, event: Event):
        query = event.message.content.strip()

        sender_id = event.message.sender_id if hasattr(event.message, 'sender_id') else None
        room_id = event.message.room_id if hasattr(event.message, 'room_id') else None
        is_group = event.message.is_group if hasattr(event.message, 'is_group') else False

        reply_id = room_id if is_group else sender_id

        if query in self.commands:  # 修改这里，确保完全匹配关键字
            news_data = self.get_news()
            response_text = '\n'.join(news_data) if news_data else '抱歉，今天没有找到无人机新闻。'
            if reply_id:
                send_txt(response_text, reply_id)
                event.bypass()
        else:
            # 当消息不匹配关键字时，不发送任何回复
            pass

    def help(self, **kwargs) -> str:
        return "输入commend命令获取最新的无人机相关新闻。"

    def will_generate_reply(self, event: Event):
        query = event.message
        return query in self.commands

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass
