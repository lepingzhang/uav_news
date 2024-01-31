import re
import requests
import schedule
import threading
import time
from bs4 import BeautifulSoup
from datetime import datetime
from plugins import register, Plugin, Event, logger, Reply, ReplyType
from utils.api import send_txt

@register
class UAVNews(Plugin):
    name = 'uav_news'
    scheduler_thread = None
    lock = threading.Lock()

    def __init__(self, config=None):
        super().__init__(config=config)
        self.target_date = datetime.now().strftime('%Y-%m-%d')
        self.commands = self.config.get('command', [])
        self.is_scheduled_push_executed = False
        if self.config.get("schedule_time"):
            if __class__.scheduler_thread is None:
                __class__.scheduler_thread = threading.Thread(target=self.start_schedule)
                __class__.scheduler_thread.daemon = True
                __class__.scheduler_thread.start()
        else:
            pass

    def get_news(self):
        self.target_date = datetime.now().strftime('%Y-%m-%d')
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
        query = re.sub(r'@\w+\s', '', query)
        sender_id = event.message.sender_id if hasattr(event.message, 'sender_id') else None
        room_id = event.message.room_id if hasattr(event.message, 'room_id') else None
        is_group = event.message.is_group if hasattr(event.message, 'is_group') else False
        reply_id = room_id if is_group else sender_id
        if any(re.fullmatch(command, query) for command in self.commands):
            news_data = self.get_news()
            response_text = "✈️无人机新闻\n\n" + ('\n'.join(news_data) if news_data else '抱歉，今天没有找到无人机新闻。')
            if reply_id:
                send_txt(response_text, reply_id)
                event.bypass()
        else:
            pass

    def start_schedule(self):
        schedule_time = self.config.get("schedule_time")
        if schedule_time:
            schedule.every().day.at(schedule_time).do(self.scheduled_push)
            while True:
                schedule.run_pending()
                time.sleep(1)

    def scheduled_push(self):
        with self.lock:
            if not self.is_scheduled_push_executed:
                self.is_scheduled_push_executed = True
                single_chat_list = self.config.get("single_chat_list", [])
                group_chat_list = self.config.get("group_chat_list", [])
                news_data = self.get_news()
                response_text = "✈️无人机新闻\n\n" + ('\n'.join(news_data) if news_data else '抱歉，今天没有找到无人机新闻。')
                if single_chat_list and all(single_chat_list):
                    for single_chat in single_chat_list:
                        send_txt(response_text, single_chat)
                if group_chat_list and all(group_chat_list):
                    for group_chat in group_chat_list:
                        send_txt(response_text, group_chat)
            else:
                pass

    def help(self, **kwargs) -> str:
        return "输入关键词获取最新的无人机新闻。"

    def will_generate_reply(self, event: Event):
        query = event.message
        return query in self.commands

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass
