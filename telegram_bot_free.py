import requests
import telegram
import feedparser
import time
import os

# Налаштування
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7578141836:AAGj_be7DOaq0wT-RL53gVDFEn_ZZMDNCXM')
CHAT_ID = os.getenv('CHAT_ID', '8142520596')
CHANNEL_ID = os.getenv('CHANNEL_ID', 'fiveleagues')

# RSS-стрічки
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/sport/football/rss.xml',
    'https://www.skysports.com/rss/12040',
    'https://e00-marca.uecdn.es/rss/futbol/primera-division.xml',
    'https://www.kicker.de/bundesliga/rss',
    'https://www.lequipe.fr/rss/football.xml'
]

# Ініціалізація бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)

def fetch_news():
    news = []
    for feed in RSS_FEEDS:
        feed_data = feedparser.parse(feed)
        for entry in feed_data.entries[:1]:  # Остання новина
            news.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link
            })
    return news

def format_post(news_item):
    comment = "👉 Журналістський вайб: Це може бути гучним трансфером, але все залежить від форми гравця. Ваша думка? 👇"
    return f"""
⚽️ {news_item['title'].upper()} 🏆
{news_item['summary'][:250]}...
🔗 Докладніше: {news_item['link']}
{comment}
>>> Докладніше про подію <<< 
✅ Підтвердити / ❌ Відхилити / ✍️ Виправити
"""

def send_news_to_user():
    news = fetch_news()
    for item in news:
        post = format_post(item)
        bot.send_message(chat_id=CHAT_ID, text=post)

def main():
    while True:
        send_news_to_user()
        time.sleep(3600)  # Перевірка кожну годину

if __name__ == '__main__':
    main()
