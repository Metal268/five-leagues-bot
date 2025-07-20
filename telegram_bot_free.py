import asyncio
import telegram
import feedparser
import os

# Налаштування
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7578141836:AAGj_be7DOaq0wT-RL53gVDFEn_ZZMDNCXM')
CHAT_ID = os.getenv('CHAT_ID', '8142520596')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@fiveleagues')  # Переконайся, що це правильний ID каналу

# RSS-стрічки для топ-5 ліг Європи
RSS_FEEDS = [
    'http://feeds.bbci.co.uk/sport/football/premier-league/rss.xml',  # АПЛ (Англія)
    'https://e00-marca.uecdn.es/rss/futbol/primera-division.xml',     # Ла Ліга (Іспанія)
    'https://www.gazzetta.it/rss/Xml/calcio.xml',                    # Серія А (Італія)
    'https://www.kicker.de/bundesliga/rss',                          # Бундесліга (Німеччина)
    'https://www.lequipe.fr/rss/football.xml'                        # Ліга 1 (Франція)
]

# Ініціалізація бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Ігнорування порту для Render
os.environ['PORT'] = '0'

async def fetch_news():
    news = []
    for feed in RSS_FEEDS:
        feed_data = feedparser.parse(feed)
        for entry in feed_data.entries[:1]:  # Беремо лише одну новину з кожної стрічки
            news.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link
            })
    return news

async def format_final_post(news_item):
    # Створюємо структурований пост за прикладом
    title = news_item['title']
    summary = news_item['summary'].replace('<p>', '').replace('</p>', '')[:250]
    
    # Поки placeholder для статистики та коментаря (можна оновити пізніше)
    stats = """
📊 Статистика (приклад):
▪️ 15 голів
▪️ 8 асистів
▪️ Найбільше ударів у лізі (117)
▪️ 2-й за очікуваними голами (xG = 21.6)
"""
    comment = """
💬 Коментар експерта:
«Тактично гнучкий, розумний, добре діє в пресингу.»
"""
    additional_info = """
📌 Що ще відомо:
▪️ Деталі трансферу уточнюються
"""

    return f"""
🔴 *{title}*

{summary}...

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
        # Ручна обробка кнопок
        offset = 0
        while True:
            updates = await bot.get_updates(offset=offset, timeout=10)
            for update in updates:
                if update.callback_query and update.callback_query.message.message_id == message.message_id:
                    query = update.callback_query
                    await query.answer()
                    if query.data == "confirm":
                        await bot.send_message(chat_id=CHANNEL_ID, text=final_post, parse_mode='Markdown')
                        await query.edit_message_text("✅ Опубліковано в @fiveleagues!")
                    elif query.data == "decline":
                        await query.edit_message_text("❌ Відхилено.")
                    elif query.data == "edit":
                        await query.edit_message_text("✍️ Введи новий текст у відповіді.")
                    offset = update.update_id + 1
                    return  # Вихід після обробки
            await asyncio.sleep(1)  # Пауза, щоб не перевантажувати API

async def main():
    while True:
        await send_news_to_user()
        await asyncio.sleep(3600)  # Перевірка кожну годину

if __name__ == '__main__':
    asyncio.run(main())
