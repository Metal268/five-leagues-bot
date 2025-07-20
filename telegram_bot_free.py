import asyncio
import telegram
import feedparser
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image  # Використовуємо Pillow замість imghdr

# Налаштування
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7578141836:AAGj_be7DOaq0wT-RL53gVDFEn_ZZMDNCXM')
CHAT_ID = os.getenv('CHAT_ID', '8142520596')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@fiveleagues')

# RSS-стрічки для топ-5 ліг Європи
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/sport/football/premier-league/rss.xml',
    'https://www.skysports.com/rss/football.xml'
]

# Ініціалізація бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Ігнорування порту для Render
os.environ['PORT'] = '0'

async def fetch_news():
    news = []
    for feed in RSS_FEEDS:
        feed_data = feedparser.parse(feed)
        for entry in feed_data.entries[:1]:
            news.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link
            })
    return news

def get_image_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        img = soup.find('img')
        return img['src'] if img and 'src' in img.attrs else None
    except:
        return None

async def get_twitter_comments(keyword):
    comments = [
        "Фанати Ліверпуля в захваті від трансферу! #LFC",
        "Експерти кажуть, що це угода століття. #TransferNews"
    ]
    return comments[0] if comments else "Коментарі відсутні"

async def format_final_post(news_item):
    title = news_item['title']
    summary = news_item['summary'].replace('<p>', '').replace('</p>', '')[:250]
    details = summary.split('.')[0] + '. Переговори тривають...'
    twitter_comment = await get_twitter_comments(title.split()[0])
    stats = """
📊 Статистика (приклад):
▪️ 15 голів
▪️ 8 асистів
▪️ Найбільше ударів у лізі
▪️ Високий xG
"""
    comment = f"""
💬 Коментар із соцмереж:
«{twitter_comment}»
"""
    additional_info = """
📌 Що ще відомо:
▪️ Угода може закритися найближчими днями
"""

    return f"""
🔴 *{title}*

{details}

{stats}
{comment}
{additional_info}

#АПЛ #ЛаЛіга #СеріяА #Бундесліга #Ліга1
"""

async def send_news_to_user():
    news = await fetch_news()
    for item in news:
        final_post = await format_final_post(item)
        keyboard = [
            [{"text": "✅ Підтвердити", "callback_data": "confirm"},
             {"text": "❌ Відхилити", "callback_data": "decline"},
             {"text": "✍️ Виправити", "callback_data": "edit"}]
        ]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        message = await bot.send_message(chat_id=CHAT_ID, text=final_post, reply_markup=reply_markup, parse_mode='Markdown')
        image_url = get_image_url(item['link'])
        if image_url:
            try:
                await bot.send_photo(chat_id=CHAT_ID, photo=image_url)
            except Exception as e:
                print(f"Помилка з фото: {e}")
        offset = 0
        while True:
            updates = await bot.get_updates(offset=offset, timeout=10)
            for update in updates:
                if update.callback_query and update.callback_query.message.message_id == message.message_id:
                    query = update.callback_query
                    await query.answer()
                    if query.data == "confirm":
                        await bot.send_message(chat_id=CHANNEL_ID, text=final_post, parse_mode='Markdown')
                        if image_url:
                            try:
                                await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url)
                            except Exception as e:
                                print(f"Помилка з фото: {e}")
                        await query.edit_message_text("✅ Опубліковано в @fiveleagues!")
                    elif query.data == "decline":
                        await query.edit_message_text("❌ Відхилено.")
                    elif query.data == "edit":
                        await query.edit_message_text("✍️ Введи новий текст у відповіді.")
                    offset = update.update_id + 1
                    return
            await asyncio.sleep(1)

async def main():
    while True:
        await send_news_to_user()
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
